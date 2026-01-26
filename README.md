# AutoCalcRule

Adds Attribute Rules to a feature class to calculate area (acres) or length (feet or miles) when features are created or their geometry is edited.

## Limitations
* Attribute rules cannot be applied to shapefiles. This tool will only work with features classes in a geodatabase.
* The rule calculates area and length using the feature class's projected coordinate system. **Ensure your data is in the correct projected coordinate system for your region.**
