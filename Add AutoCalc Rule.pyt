# -*- coding: utf-8 -*-
# Authors: code - Aaron Wright aaron.wright@usda.gov | initial workflow - Tyler Harris
# Created 1/07/2026

import arcpy


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [autoCalcAcresRule, autoCalcMilesRule, autoCalcFeetRule]


class autoCalcAcresRule:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add AutoCalc Acres Rule"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""
        inFc = arcpy.Parameter(
            name='in_features',
            displayName='Input Feature Class',
            datatype='GPFeatureLayer',
            direction='Input',
            parameterType='Required'
        )

        acresField = arcpy.Parameter(
            name='acresField',
            displayName='Acres Field',
            datatype='GPString',
            direction='Input',
            parameterType='Optional'
        )
        
        newField = arcpy.Parameter(
            name='new_field',
            displayName='Create new acres field',
            datatype='GPBoolean',
            direction='Input',
            parameterType='Optional'
        )

        nfName = arcpy.Parameter(
            name='newFieldName',
            displayName='New Field',
            datatype='Field',
            direction='Input',
            parameterType='Optional',
            enabled='False'
        )

        initCalc = arcpy.Parameter(
            name='initialCalculation',
            displayName='Perform initial calculation on existing features',
            datatype='GPBoolean',
            direction='Input',
            parameterType='Optional'
        )

        nfName.value = 'GIS_Acres'

        params = [inFc, acresField, newField, nfName, initCalc]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[2].value is True:
            parameters[1].enabled = False
            parameters[3].enabled = True
        else:
            parameters[1].enabled = True
            parameters[3].enabled = False

        if parameters[0].altered and not parameters[0].hasBeenValidated:
            inputFC = parameters[0].value
            field_names = []
            for f in arcpy.ListFields(inputFC):
                if f.type not in ['OID', 'Geometry', 'GlobalID'] and f.name not in ['Shape_Area', 'Shape_Length']:
                    field_names.append(f.name)
            parameters[1].filter.list = sorted(field_names)

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        if parameters[1].enabled is True and parameters[1].value is None:
            parameters[1].setErrorMessage("A field must be selected or a new field created.", 530)
        if parameters[0].altered and not parameters[0].hasBeenValidated:
            if arcpy.Describe(parameters[0]).dataType != "FeatureLayer":
                descP0 = arcpy.Describe(parameters[0].value)
            else:
                descP0 = arcpy.Describe(parameters[0].value).dataElement
            if descP0.shapeType != "Polygon":
                parameters[0].setErrorMessage("Feature Class must be a 'Polygon' feature class.")
            elif descP0.dataType != "FeatureClass":
                parameters[0].setErrorMessage(f"Must be a feature class within a GDB. Attribute Rules cannot be applied to a shapefile.")
            elif descP0.spatialReference.type != "Projected" or descP0.spatialReference.factoryCode == 3857:
                parameters[0].setErrorMessage("Input feature class is not in a Projected Coordinate System, or is in 'WGS 84 Web Mercator (Auxiliary Sphere)'. The rule added by this tool uses the input feature class projection to calculate area.")
            else:
                parameters[0].clearMessage()
   

        if parameters[1].altered and not parameters[1].hasBeenValidated:
            fldName = parameters[1].value
            fld = arcpy.ListFields(parameters[0].value, fldName)[0]
            if fld.type not in ['Single', 'Double']:
                parameters[1].setErrorMessage("Field 'Type' must be 'Float' or 'Double'.") 
            else:
                parameters[1].clearMessage()

        if parameters[0].value and (parameters[3].enabled is True and parameters[3].value):
            if parameters[3].valueAsText.replace(' ', '_') in [f.name for f in arcpy.ListFields(parameters[0].valueAsText)]:
                parameters[3].setErrorMessage("This field name already exists, please specify a new field name.")
            else:
                parameters[3].clearMessage()


        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            #Parameters as variables
            inputFC = parameters[0].valueAsText
            fldNm = parameters[1].valueAsText
            newFld = parameters[2].value
            newFldNm = parameters[3].valueAsText.replace(' ', '_')
            inCalc = parameters[4].value

            #Check inputFC for Global ID's, if none add Global ID's
            desc = arcpy.Describe(inputFC)
            if desc.hasGlobalID is False:
                arcpy.management.AddGlobalIDs(inputFC)
            
            #If new acres field is checked, define fldNm var from newFldNm, and add field with user defined name
            if newFld is True:
                fldNm = newFldNm
                arcpy.management.AddField(inputFC, fldNm, 'Double')

            #If initial calculation is checked, perform calculation on existing features
            if inCalc is True:
                arcpy.management.CalculateGeometryAttributes(inputFC, [[fldNm, "AREA_GEODESIC"]], "", "ACRES")

            #Add attribute rule to calculate acres when a feature is added or edited
            ruleNm = "AutoCalc Acres"
            ruleExp = "AreaGeodetic($feature, 'acres', 'ShapePreserving')"
            trgFld = "SHAPE"
            arcpy.management.AddAttributeRule(inputFC, ruleNm, 'CALCULATION', ruleExp, 'EDITABLE', "INSERT;UPDATE", "", "", "", "", fldNm, "", 'NOT_BATCH', "", "", trgFld)
        except Exception as e:
            arcpy.AddError(f"An error occurred: {e}")

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    
class autoCalcMilesRule:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add AutoCalc Miles Rule"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""
        inFc = arcpy.Parameter(
            name='in_features',
            displayName='Input Feature Class',
            datatype='GPFeatureLayer',
            direction='Input',
            parameterType='Required'
        )

        milesField = arcpy.Parameter(
            name='milesField',
            displayName='Miles Field',
            datatype='GPString',
            direction='Input',
            parameterType='Optional'
        )
        
        newField = arcpy.Parameter(
            name='new_field',
            displayName='Create new miles field',
            datatype='GPBoolean',
            direction='Input',
            parameterType='Optional'
        )

        nfName = arcpy.Parameter(
            name='newFieldName',
            displayName='New Field',
            datatype='Field',
            direction='Input',
            parameterType='Optional',
            enabled='False'
        )

        initCalc = arcpy.Parameter(
            name='initialCalculation',
            displayName='Perform initial calculation on existing features',
            datatype='GPBoolean',
            direction='Input',
            parameterType='Optional'
        )

        nfName.value = 'GIS_Miles'
        
        params = [inFc, milesField, newField, nfName, initCalc]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[2].value is True:
            parameters[1].enabled = False
            parameters[3].enabled = True
        else:
            parameters[1].enabled = True
            parameters[3].enabled = False

        if parameters[0].altered and not parameters[0].hasBeenValidated:
            inputFC = parameters[0].value
            field_names = []
            for f in arcpy.ListFields(inputFC):
                if f.type not in ['OID', 'Geometry', 'GlobalID'] and f.name not in ['Shape_Area', 'Shape_Length']:
                    field_names.append(f.name)
            parameters[1].filter.list = sorted(field_names)

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        if parameters[1].enabled is True and parameters[1].value is None:
            parameters[1].setErrorMessage("A field must be selected or a new field created.", 530)
        if parameters[0].altered and not parameters[0].hasBeenValidated:
            if arcpy.Describe(parameters[0]).dataType != "FeatureLayer":
                descP0 = arcpy.Describe(parameters[0].value)
            else:
                descP0 = arcpy.Describe(parameters[0].value).dataElement
            if descP0.shapeType not in ["Polyline", "Line"]:
                parameters[0].setErrorMessage("Feature Class must be a 'Line' feature class.")
            elif descP0.dataType != "FeatureClass":
                parameters[0].setErrorMessage(f"Must be a feature class within a GDB. Attribute Rules cannot be applied to a shapefile.")
            elif descP0.spatialReference.type != "Projected" or descP0.spatialReference.factoryCode == 3857:
                parameters[0].setErrorMessage("Input feature class is not in a Projected Coordinate System, or is in 'WGS 84 Web Mercator (Auxiliary Sphere)'. The rule added by this tool uses the input feature class projection to calculate area.")
            else:
                parameters[0].clearMessage()


        if parameters[1].altered and not parameters[1].hasBeenValidated:
            fldName = parameters[1].value
            fld = arcpy.ListFields(parameters[0].value, fldName)[0]
            if fld.type not in ['Single', 'Double']:
                parameters[1].setErrorMessage("Field 'Type' must be 'Float' or 'Double'.") 
            else:
                parameters[1].clearMessage()

        if parameters[0].value and (parameters[3].enabled is True and parameters[3].value):
            if parameters[3].valueAsText.replace(' ', '_') in [f.name for f in arcpy.ListFields(parameters[0].valueAsText)]:
                parameters[3].setErrorMessage("This field name already exists, please specify a new field name.")
            else:
                parameters[3].clearMessage()


        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            #Parameters as variables
            inputFC = parameters[0].valueAsText
            fldNm = parameters[1].valueAsText
            newFld = parameters[2].value
            newFldNm = parameters[3].valueAsText.replace(' ', '_')
            inCalc = parameters[4].value

            #Check inputFC for Global ID's, if none add Global ID's
            desc = arcpy.Describe(inputFC)
            if desc.hasGlobalID is False:
                arcpy.management.AddGlobalIDs(inputFC)
            
            #If new acres field is checked, define fldNm var from newFldNm, and add field with user defined name
            if newFld is True:
                fldNm = newFldNm
                arcpy.management.AddField(inputFC, fldNm, 'Double')

            #If initial calculation is checked, perform calculation on existing features
            if inCalc is True:
                arcpy.management.CalculateGeometryAttributes(inputFC, [[fldNm, "LENGTH_GEODESIC"]], "MILES_INT")

            #Add attribute rule to calculate miles when a feature is added or edited
            ruleNm = "AutoCalc Miles"
            ruleExp = "LengthGeodetic($feature, 'miles', 'ShapePreserving')"
            trgFld = "SHAPE"
            arcpy.management.AddAttributeRule(inputFC, ruleNm, 'CALCULATION', ruleExp, 'EDITABLE', "INSERT;UPDATE", "", "", "", "", fldNm, "", 'NOT_BATCH', "", "", trgFld)

        except Exception as e:
            arcpy.AddError(f"An error occurred: {e}")

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

class autoCalcFeetRule:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Add AutoCalc Feet Rule"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""
        inFc = arcpy.Parameter(
            name='in_features',
            displayName='Input Feature Class',
            datatype='GPFeatureLayer',
            direction='Input',
            parameterType='Required'
        )

        FeetField = arcpy.Parameter(
            name='feetField',
            displayName='Feet Field',
            datatype='GPString',
            direction='Input',
            parameterType='Optional'
        )
        
        newField = arcpy.Parameter(
            name='new_field',
            displayName='Create new feet field',
            datatype='GPBoolean',
            direction='Input',
            parameterType='Optional'
        )

        nfName = arcpy.Parameter(
            name='newFieldName',
            displayName='New Field',
            datatype='Field',
            direction='Input',
            parameterType='Optional',
            enabled='False'
        )

        initCalc = arcpy.Parameter(
            name='initialCalculation',
            displayName='Perform initial calculation on existing features',
            datatype='GPBoolean',
            direction='Input',
            parameterType='Optional'
        )
        
        nfName.value = 'GIS_Feet'
        
        params = [inFc, FeetField, newField, nfName, initCalc]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[2].value is True:
            parameters[1].enabled = False
            parameters[3].enabled = True
        else:
            parameters[1].enabled = True
            parameters[3].enabled = False

        if parameters[0].altered and not parameters[0].hasBeenValidated:
            inputFC = parameters[0].value
            field_names = []
            for f in arcpy.ListFields(inputFC):
                if f.type not in ['OID', 'Geometry', 'GlobalID'] and f.name not in ['Shape_Area', 'Shape_Length']:
                    field_names.append(f.name)
            parameters[1].filter.list = sorted(field_names)

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        if parameters[1].enabled is True and parameters[1].value is None:
            parameters[1].setErrorMessage("A field must be selected or a new field created.", 530)
        if parameters[0].altered and not parameters[0].hasBeenValidated:
            if arcpy.Describe(parameters[0]).dataType != "FeatureLayer":
                descP0 = arcpy.Describe(parameters[0].value)
            else:
                descP0 = arcpy.Describe(parameters[0].value).dataElement
            if descP0.shapeType not in ["Polyline", "Line"]:
                parameters[0].setErrorMessage("Feature Class must be a 'Line' feature class.")
            elif descP0.dataType != "FeatureClass":
                parameters[0].setErrorMessage(f"Must be a feature class within a GDB. Attribute Rules cannot be applied to a shapefile.")
            elif descP0.spatialReference.type != "Projected" or descP0.spatialReference.factoryCode == 3857:
                parameters[0].setErrorMessage("Input feature class is not in a Projected Coordinate System, or is in 'WGS 84 Web Mercator (Auxiliary Sphere)'. The rule added by this tool uses the input feature class projection to calculate area.")
            else:
                parameters[0].clearMessage()


        if parameters[1].altered and not parameters[1].hasBeenValidated:
            fldName = parameters[1].value
            fld = arcpy.ListFields(parameters[0].value, fldName)[0]
            if fld.type not in ['Single', 'Double']:
                parameters[1].setErrorMessage("Field 'Type' must be 'Float' or 'Double'.") 
            else:
                parameters[1].clearMessage()

        if parameters[0].value and (parameters[3].enabled is True and parameters[3].value):
            if parameters[3].valueAsText.replace(' ', '_') in [f.name for f in arcpy.ListFields(parameters[0].valueAsText)]:
                parameters[3].setErrorMessage("This field name already exists, please specify a new field name.")
            else:
                parameters[3].clearMessage()


        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            #Parameters as variables
            inputFC = parameters[0].valueAsText
            fldNm = parameters[1].valueAsText
            newFld = parameters[2].value
            newFldNm = parameters[3].valueAsText.replace(' ', '_')
            inCalc = parameters[4].value

            #Check inputFC for Global ID's, if none add Global ID's
            desc = arcpy.Describe(inputFC)
            if desc.hasGlobalID is False:
                arcpy.management.AddGlobalIDs(inputFC)
            
            #If new acres field is checked, define fldNm var from newFldNm, and add field with user defined name
            if newFld is True:
                fldNm = newFldNm
                arcpy.management.AddField(inputFC, fldNm, 'Double')

            #If initial calculation is checked, perform calculation on existing features
            if inCalc is True:
                arcpy.management.CalculateGeometryAttributes(inputFC, [[fldNm, "LENGTH_GEODESIC"]], "FEET_INT")

            #Add attribute rule to calculate feet when a feature is added or edited
            ruleNm = "AutoCalc Feet"
            ruleExp = "LengthGeodetic($feature, 'feet', 'ShapePreserving')"
            trgFld = "SHAPE"
            arcpy.management.AddAttributeRule(inputFC, ruleNm, 'CALCULATION', ruleExp, 'EDITABLE', "INSERT;UPDATE", "", "", "", "", fldNm, "", 'NOT_BATCH', "", "", trgFld)

        except Exception as e:
            arcpy.AddError(f"An error occurred: {e}")
            
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return