# TacTipGenerator
Programs to generate TacTip geometry (skin and pins) with circular pin pattern (hexagonal base layer) using the Fusion 360 API.

## Contents
- markerGenerator/**markerGenerator.py** - Code to generate marker geometry
- skinGenerator/**skinGenerator.py** - Code to generate skin geometry
- **pinPoint3Dmapping.pdf** - pdf outlining mathematics used in calculating 3D pin co-ordinates

As mentioned in the description, this code uses the Fusion 360 API to generate the geometry and thus you need a copy of Fusion 360. To read more about the Fusion 360 API see the documentation [here](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-03033DE6-AD8E-46B3-B4E6-DADA8D389E4E) (under 'programming interface' in the dropdown list).

The Fusion 360 API uses VS Code as an editing environment so this should also be installed. 

## How to use
1. Clone this repository, then run Fusion 360 and from the tab menu at the top navigate to TOOLS/ADD-INS.
2. When in the 'Scripts and Add-Ins' menu, under the 'Scripts' tab select the green plus sign next to the 'My Scripts' heading.
3. Navigate to the directory the repo was cloned to and select the 'markerGenerator' folder.
4. Repeat steps 2 & 3 now for the 'skinGenerator' folder.
5. To generate skin geometry: whilst still in the 'Scripts and Add-Ins' menu in Fusion, select 'skinGenerator' which should now appear under the 'My Scripts' heading with the Python logo next to it, then click 'Edit'. This should load up the 'skinGenerator.py' script in VS Code.
6. In the Python script, change the parameters at the top of the 'run' function to suit the geometry you wish to generate. **NOTE** The Fusion 360 API for some reason requires dimensions to be defined in centimetres so make sure to check your units.
7. **Save the script**  
8. Go back to the 'Scripts and Add-Ins' menu in Fusion, select 'skinGenerator' and hit 'Run'. The shelled hemispherical geometry with 1/6 of the surface points plotted should appear with a dialog box prompting the user to select the inside face. Press OK and pick the inside face of the hemisphere with the cursor, after which the geometry should be generated.
9. To generate marker geometry: repeat steps 5 - 8 this time using 'markerGenerator', following instructions of the dialog boxes in Fusion as directed. **NOTE** Ensure the parameters used in generating the skin are the same when generating the markers. The only additional parameter in markerGenerator is the marker height.

## How it works
Both scripts work in a similar way. To make for a lighter rendering job, the 6 planes of symmetry of the pattern are used so that only 1/6 of the pins/markers actually need to be extruded as they can then be patterned around the z-axis to complete the geometry. This results in a lighter model as the patterned features inherit from the extruded features and prevents the program from crashing:
### skinGenerator:
- Calculate 3D pin co-ordinates from defined geometric parameters (as per pinPoint3Dmapping.pdf)
- Create overall hemispherical geometry
- Shell hemisphere to defined thickness
- Plot centre point and 1/6 of pin points to the surface (user selects the surface)
- At each point create a construction plane tangent to the inside surface of the hemisphere (with the point as the origin)
- On each construction plane sketch and extrude a pin to the defined dimensions
- Select all extruded pins and put them into a 6x circular pattern about the z-axis to complete the geometry

### markerGenerator:
- Calculate 3D pin co-ordinates from defined geometric parameters (as per pinPoint3Dmapping.pdf)
- Create overall hemispherical geometry
- Shell hemisphere to defined thickness (which now includes the height of the pins generated in the skin)
- Plot centre point and 1/6 of pin points to the surface (user selects the surface)
-  At each point create a construction plane tangent to the inside surface of the hemisphere (with the point as the origin)
- On each construction plane sketch and extrude a **marker** to the defined dimensions
- Select all extruded markers and put them into a 6x circular pattern about the z-axis
- User prompted to select original hemispherical geometry, which removes it from the design leaving only the markers in the correct positions, completing the geometry

## I managed to generate the geometry - now what??

The Fusion 360 API was used in this instance mostly as it's "create plane tangent to surface at point" feature really streamlines this process. Unfortunately, the same cannot be said for Fusion's assembly UI. Consequently, I would recommend exporting your freshly generated TacTip skin and marker geometries (in Fusion: File>Export) as .STEP files and loading them into your favourite CAD package. If you're using SolidWorks, you should be able to open the .STEP files and simply save them as SolidWorks parts. 

Enjoy!
 

