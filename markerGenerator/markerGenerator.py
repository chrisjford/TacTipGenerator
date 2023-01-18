#Author- C.J. Ford
#Description- Code to generate TacTip geometry with circular pin pattern (hexagonal base layer) using the Fusion 360 API.

import adsk.core, adsk.fusion, adsk.cam, traceback, math, time, os

def pointsCalculator(n, x1, r, t, h):
    # Function to calculate 3D co-ordinates of pin positions on skin surface

    # Iterators:
    i = 1
    k = 1
    theta = math.asin(x1/(r-t)) # ZX angle
    points = []
    points.append((0,0,(r-t-h))) # Plot centre pin point

    while i <= n:
        m = 6*i
        
        while k <= m/6:
            alpha = (2*math.pi)/m   # XY angle
            x0 = (r-t-h)*math.sin(i*theta)
            z = (r-t-h)*math.cos(i*theta)

            point = (x0*math.sin(k*alpha), x0*math.cos(k*alpha), z)

            points.append(point)

            k = k+1

        k=1
        i = i+1
    
    return points

def run(context):
    ui = None
    try:
        # Set up environment:
        app = adsk.core.Application.get()   # Get application (program)
        ui  = app.userInterface     # Get UI from application
        design = adsk.fusion.Design.cast(app.activeProduct)     # Define we are in the design environment with the active product being the active design environment (i.e the open file)
        rootComp = design.rootComponent     # Top level component
        sketches = rootComp.sketches    # Gets the sketches contained in the root component
        pinSketches = rootComp.sketches
        features = rootComp.features
        removeFeatures = features.removeFeatures

        r = 10.2/10    # TacTip radius (in cm)
        h= 0.5/10 # Pin height (cm)
        h_m = 0.25/10 # Marker height (cm)
        t = 1/10     # Skin thickness (in cm)
        n = 8  # Number of pin layers
        x1 = 1.5/10    # Initial x-distance (in cm)
        pointList = pointsCalculator(n, x1, r, t, h)


        # Create profile for hemispherical revolve:
        sketch = sketches.add(rootComp.xYConstructionPlane)  # Creates the empty sketch on   the xY plane 
            #Draw circular profile:
        circles = sketch.sketchCurves.sketchCircles     # Analgous to selecting the 'draw circle' tool, attached to the created sketch
        circle =  circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), r)   # Draws a circle of radius 'r' from the defined 3D point on the sketch

            #Draw line for axis of revolution: 
        lines = sketch.sketchCurves.sketchLines     # Analagous to selecting the 'draw line' tool
        axisLine = lines.addByTwoPoints(adsk.core.Point3D.create(-r, 0, 0), adsk.core.Point3D.create(r, 0, 0))  # Draws a line in the sketch between the two co-ordinates.

            # Extract circle profile from sketch:
        prof = sketch.profiles.item(0)  # item(0) as the circle was the first sketch entity created. item(1) would be the line created in the previous step.

        # Create revolved hemisphere:
        revolves = rootComp.features.revolveFeatures    # Defines revolve features in the root component
        revInput = revolves.createInput(prof, axisLine, adsk.fusion.FeatureOperations.NewComponentFeatureOperation)     # Adds a revolve input item to revolve features
        angle = adsk.core.ValueInput.createByReal(math.pi)  # Defines revolve angle, in this case pi as we want a hemisphere
        revInput.setAngleExtent(False, angle)

        # Create the extrusion.
        ext = revolves.add(revInput)

        # Create a collection of entities for shell
        entities = adsk.core.ObjectCollection.create()
        entities.add(ext.endFaces.item(0))

        # Create a shell feature
        shellFeats = features.shellFeatures
        isTangentChain = False
        shellFeatureInput = shellFeats.createInput(entities, isTangentChain)
        thickness = adsk.core.ValueInput.createByReal(t+h)
        shellFeatureInput.insideThickness = thickness
        shellFeats.add(shellFeatureInput)

        # create another sketch
        sketch2 = sketches.add(rootComp.xYConstructionPlane)

        # Plot pin position points:
        pinPoints = sketch2.sketchPoints
        for point in pointList:
            pinPoints.add(adsk.core.Point3D.create(point[0], point[1], point[2]))

        # Get construction planes & extrudes
            planes = rootComp.constructionPlanes
            extrudes = rootComp.features.extrudeFeatures
            planeInput = planes.createInput()
            
        # Select inside face of shell to apply pins:
        ui.messageBox('Select inside face of skin for pin application.')
            #User input:
        faceSel = ui.selectEntity('Select a face.', 'Faces')
        i = 0
        if faceSel:
            insideFace = adsk.fusion.BRepFace.cast(faceSel.entity)
            # Apply tangent planes on inside skin surface at all pin points:
            for pinPoint in pinPoints:
                if i==0:
                    i=i+1
                    pass
                else:
                    planeInput.setByTangentAtPoint(insideFace, pinPoint)
                    planes.add(planeInput)
                    i = i+1
            # Add pin extrusions to each tangent plane:
            for plane in planes:
                sketch = pinSketches.add(plane)
                circles = sketch.sketchCurves.sketchCircles
                circle = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 0.3/10)
                # Comment/uncomment for hollow pin feature:
                #circle2 = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), 0.1/10)

                prof = sketch.profiles.item(0)
                distance = adsk.core.ValueInput.createByReal(h_m)
                extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Create an entity input for features to be patterned:
        patternInputEntities = adsk.core.ObjectCollection.create()
        i = 0
        # Add all pin extrusions to entity input:
        for extrude in extrudes:
            patternInputEntities.add(rootComp.bRepBodies.item(i))
            i=i+1
        # Configure circular pattern features:
        circularFeats = rootComp.features.circularPatternFeatures

        # Create circular pattern input to be applied about the z-axis:
        circularFeatInput = circularFeats.createInput(patternInputEntities, rootComp.zConstructionAxis)

        # Set pattern feature quantity (6 required for hexagonal origin pattern):
        circularFeatInput.quantity = adsk.core.ValueInput.createByReal(6)

        # Set the angle of the circular pattern
        circularFeatInput.totalAngle = adsk.core.ValueInput.createByString('360 deg')

        # Create the circular pattern
        circularFeat = circularFeats.add(circularFeatInput)

        # Select revolve/shell component to remove it, leaving just the markers:
        ui.messageBox('Select hemispherical body for removal.')
            #User input:
        bodySel = ui.selectEntity('Select hemispherical body.', 'Occurrences')
        if bodySel:
            # Create remove feature
            removeFeat = removeFeatures.add(bodySel.entity)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
