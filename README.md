# AutoCalcRule

Adds Attribute Rules to a feature class to calculate area (acres) or length (feet or miles) when features are created or their geometry is edited.

## What this does
This repository contains a Python script/tool that adds **ArcGIS Attribute Rules** to a geodatabase feature class so that:
- **Polygon** features automatically calculate **area (acres)**
- **Polyline** features automatically calculate **length (feet or miles)**

The rules run when features are **created** and when **geometry is edited**, helping keep derived measurements consistent.

## Requirements
- ArcGIS Pro (or an ArcGIS Python environment with `arcpy` available)
- A **file geodatabase** or **enterprise geodatabase** feature class
- A projected coordinate system appropriate for your area of interest

> Note: This repo is 100% Python and relies on Esri's `arcpy` for geodatabase/attribute rule operations.

## Usage (high level)
1. Open an ArcGIS Pro Python environment.
2. Run the provided script/tool against a target feature class.
3. Confirm the attribute rule(s) were added in **Catalog > Feature Class > Attribute Rules**.
4. Create/edit features and verify the area/length fields update as expected.

If the script supports parameters (feature class path, units, field names, etc.), pass those per the script header/docstring.

## Limitations
- Attribute rules **cannot** be applied to shapefiles. This tool will only work with feature classes in a geodatabase.
- The rule calculates area and length using the feature class's **projected coordinate system**. **Ensure your data is in the correct projected coordinate system for your region.**

## Contributing
Issues and pull requests are welcome. Please include:
- ArcGIS Pro / Enterprise version
- Geodatabase type (file vs enterprise)
- Repro steps and any error output

## License
See the repository for license information (or add a LICENSE file if one is not yet present).