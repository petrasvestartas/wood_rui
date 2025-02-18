import Rhino
import System
from typing import Union
import ast
import wood_rui


class Element():
    """
    Converts RhinoObject and its userstrings to geometry attributes.
    
    Element represents a Rhino Group objects made from two geometries:
    a) A Brep of Mesh with user strings that contain information about features, axis, radii, volumes, thickness, and joints.
    b) A polyline with three points that represents the plane of the group.
    This class helps to convert user strings to a python class with attributes and methods to manipulate the group.
    """
    def __init__(self, geometry_plane):

        self.geometry_plane : tuple[Rhino.DocObjects.RhinoObject, Rhino.Geometry.Plane] = geometry_plane  # no need to be implemented



    def _polyline_obj_to_plane(self, polyline_obj):
        polyline_curve = polyline_obj.Geometry
        if polyline_curve.PointCount == 3:  # Ensure it has exactly 3 points
            polyline = polyline_curve.ToPolyline()
            origin = polyline[1]
            x_axis = polyline[0] - polyline[1]
            y_axis = polyline[2] - polyline[1]  # Corrected y-axis calculation
            return Rhino.Geometry.Plane(origin, x_axis, y_axis)
        return Rhino.Geometry.Plane.Unset

    @property
    def plane(self):

        polyline_curve = self.geometry_plane[1].Geometry
        if polyline_curve.PointCount == 3:  # Ensure it has exactly 3 points
            polyline = polyline_curve.ToPolyline()
            origin = polyline[1]
            x_axis = polyline[0] - polyline[1]
            y_axis = polyline[2] - polyline[1]  # Corrected y-axis calculation
            return Rhino.Geometry.Plane(origin, x_axis, y_axis)
        return Rhino.Geometry.Plane.Unset
    
    def plane_axes(self, scale=1):
        plane = self.plane
        line0 = Rhino.Geometry.Line(p0, p0 + plane.XAxis * scale)
        line1 = Rhino.Geometry.Line(p0, p0 + plane.YAxis * scale)
        line2 = Rhino.Geometry.Line(p0, p0 + plane.ZAxis * scale)
        return [line0, line1, line2]
    
    @property
    def transformation(self):
        return Rhino.Geometry.Transform.PlaneToPlane(self.plane, Rhino.Geometry.Plane.WorldXY)
    
    @property
    def transformation_inverse(self):
        return Rhino.Geometry.Transform.PlaneToPlane(Rhino.Geometry.Plane.WorldXY, self.plane)
    
    @property
    def geometry(self):
        return self.geometry_plane[0].Geometry

    @property
    def features_count(self):
        count = 0
        string_dictionary = self.geometry_plane[0].Attributes.GetUserStrings()
        for key in string_dictionary:
            if "feature" in key:
                count += 1
        return count

    @property
    def features(self):
    
        geometries = []
        string_dictionary = self.geometry_plane[0].Attributes.GetUserStrings()
        for key in string_dictionary:
            if "feature" in key:
                value = string_dictionary[key]  # GetValues returns a list of values for the key
                geometry = Rhino.Geometry.GeometryBase.FromJSON(value)
                geometry.Transform(self.transformation)
                geometries.append(geometry)
        return geometries
    
    @features.setter
    def features(self, value):
        feature_count = self.features_count
        self._features = value
        for idx, geometry in enumerate(value):
            opts = Rhino.FileIO.SerializationOptions()
            opts.WriteUserData = True
            json = geometry.ToJSON(opts)
            obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
            obj.Attributes.SetUserString(f"feature_{feature_count+idx}", json)
            obj.CommitChanges()

    def clear_features(self):
        for key in self.geometry_plane[0].Attributes.GetUserStrings():
            if "feature" in key:
                self.geometry_plane[0].Attributes.DeleteUserString(key)

    @property
    def element_type(self):
        return self.geometry_plane[0].Attributes.GetUserString("element_type")
    
    @element_type.setter
    def element_type(self, value):
        self._element_type = value
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("element_type", value)
        obj.CommitChanges()

    @property
    def index(self):
        return int(self.geometry_plane[0].Attributes.GetUserString("index"))

    @index.setter
    def index(self, value):
        self._index = value
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("index", str(value))
        obj.CommitChanges()

    @property
    def neighbours(self):
        value = self.geometry_plane[0].Attributes.GetUserString("neighbours")
        return ast.literal_eval(value)

    @neighbours.setter
    def neighbours(self, value):
        self._neighbours = value
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("neighbours", str(value))
        obj.CommitChanges()

    @property
    def axes(self):
        value = self.geometry_plane[0].Attributes.GetUserString("axes")
        list = ast.literal_eval(value)
        polylines = []
        for l in list:
            polyline = Rhino.Geometry.Polyline()
            for i in range(0, len(l), 3):
                polyline.Add(Rhino.Geometry.Point3d(l[i], l[i+1], l[i+2]))
            polyline.transform(self.transformation)
            polylines.append(polyline)
        return polylines

    @axes.setter
    def axes(self, value):
        self._axes = value
        polylines_coordinates = []
        for polyline in value:
            polyline_transformed = polyline.Duplicate()
            polyline_transformed.transform(self.transformation_inverse)
            coordinates = []
            for i in range(polyline_transformed.Count):
                coordinates.extend([polyline_transformed[i].X, polyline_transformed[i].Y, polyline_transformed[i].Z])
            polylines_coordinates.append(coordinates)

        str_axes = str(polylines_coordinates)

        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("axes", str_axes)
        obj.CommitChanges()
    
    @property
    def radii(self):
        value = self.geometry_plane[0].Attributes.GetUserString("radii")
        list = ast.literal_eval(value)
        return list
    
    @radii.setter
    def radii(self, value):
        self._radii = value
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("radii", str(value))
        obj.CommitChanges()

    @property
    def thickness(self):
        value = self.geometry_plane[0].Attributes.GetUserString("thickness")
        return float(value)
    
    @thickness.setter
    def thickness(self, value):
        self._thickness = value
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("thickness", str(value))
        obj.CommitChanges()
    
    @property
    def volumes(self):
        value = self.geometry_plane[0].Attributes.GetUserString("volumes")
        list3 = ast.literal_eval(value)
        
        # convert triple nested lists to polylines
        polylines_list = []
        for list2 in list3:
            polylines = []
            for list1 in list2:
                polyline = Rhino.Geometry.Polyline()
                for i in range(0, len(list1), 3):
                    polyline.Add(Rhino.Geometry.Point3d(list1[i], list1[i+1], list1[i+2]))
                polyline.transform(self.transformation)
                polylines.append(polyline)
            polylines_list.append(polylines)
        
        return polylines_list
    
    @volumes.setter
    def volumes(self, value):
        self._volumes = value

        # Write polylines to user strings
        polylines_coordinates = []
        for i in range(0, len(value), 2):

            polyline0 = Rhino.Geometry.Polyline(value[i])
            polyline0.transform(self.transformation_inverse)

            polyline1 = Rhino.Geometry.Polyline(value[i+1])
            polyline1.transform(self.transformation_inverse)

            polyline_coordinates0 = []
            for j in range(polyline0.Count):
                polyline_coordinates0.extend([polyline0[j].X, polyline0[j].Y, polyline0[j].Z])
            
            polyline_coordinates1 = []
            for j in range(polyline1.Count):
                polyline_coordinates1.extend([polyline1[j].X, polyline1[j].Y, polyline1[j].Z])

            polylines_coordinates.append([polyline_coordinates0, polyline_coordinates1])

        str_volumes = str(polylines_coordinates)

        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("volumes", str_volumes)
        obj.CommitChanges()
    
    @property
    def insertion(self):
        value = self.geometry_plane[0].Attributes.GetUserString("insertion")

        if value == "-" or value is None:
            return [[] for _ in range(len(self.volumes))]

        list_values = ast.literal_eval(value)
        lists_vectors = []
        for l in list_values:
            vectors = []
            for i in range(0, len(l), 3):
                vectors.append(Rhino.Geometry.Vector3d(l[i], l[i+1], l[i+2]))
            lists_vectors.append(vectors)
        return lists_vectors

    @insertion.setter
    def insertion(self, value):


        list_coordinates = []
        for list_vectors in value:
            coordinates = []
            for vector in list_vectors:
                coordinates.extend([vector.X, vector.Y, vector.Z])
            list_coordinates.append(coordinates)

        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("insertion", str(coordinates))
        obj.CommitChanges()
    
    @property
    def joint_types(self):
        value = self.geometry_plane[0].Attributes.GetUserString("joint_types")

        if value == "-" or value is None:
            return [[] for _ in range(len(self.volumes))]

        list_values = ast.literal_eval(value)
        return list_values
    
    @joint_types.setter
    def joint_types(self, value):
        self._joint_types = value
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("joint_types", str(value))
        obj.CommitChanges()
            

    @staticmethod
    def get_first_axes(elements):
        return [element.axes[0] for element in elements]

    @staticmethod
    def get_first_radii(elements):
        return [element.radii[0] for element in elements]




    @staticmethod
    def add_element(
            shape : Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh],
            layer_name: str = "my_model",
            name : str = "beam",
            index : int = -1,
            neighbours : list[int] = [],
            features : list[Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh]] = [], 
            pair_polyline : list[Rhino.Geometry.Polyline] = [],
            pair_polyline_merged : list[Rhino.Geometry.Polyline] = [],
            axes : list[Rhino.Geometry.Polyline] = [],
            radii : list[list[float]] = [],
            thickness : float = 0.0,
            insertion : list[list[Rhino.Geometry.Line]] = [],
            joint_types : list[Rhino.Geometry.TextDot] = []
    ) -> None:
        """ Add element with all its attributes for the wood joinery solver. 

        Parameters
        ----------
        shape : Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh]
            The shape of the element. Final geometry is represented by one solid object.
        layer_name : str
            The name of the layer to add the geometry to.
        name : str
            The name of the element e.g. beam or plate.
        index : int
            The index of the element. Index is important when element are selected randomly.
        neighbours : list[int]
            The indices of the neighbouring elements.
        features : list[Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh]]
            The features of the element. Features are represented by multiple solid objects.
        pair_polyline : list[Rhino.Geometry.Polyline]
            The pair of polylines that represent the top and bottom of the element.
        pair_polyline_merged : list[Rhino.Geometry.Polyline]
            The pair of polylines that represent the top and bottom with joinery, specific to plates.
        axes : list[Rhino.Geometry.Polyline]
            The axes of the element.
        radii : list[list[float]]
            The radii of the axes.
        thickness : float
            The thickness of the element.
        insertion : list[Line]
            The insertion vectors of the element.
        joint_types : list[TextDot]
            The joints found by searching through the text dots.
        
        """

        ######################################################################
        # Add shape to Rhino document add assign plane on WorldXY.
        #   Create a layer: compas_wood::layer_name::element.
        #   Add geometry to the Rhino Canvas.
        #   Add a polyline to the Rhino Canvas to represnt a plane.
        ######################################################################

        # Create layer or find the existing one.
        layer_index = wood_rui.ensure_layer_exists("compas_wood", layer_name, name, System.Drawing.Color.Red)
        
        # Add the geometry to the Rhino document.
        if not shape:
            Rhino.RhinoApp.WriteLine("Attention: no shape to add.")
            return
        
        obj_guid = None

        if isinstance(shape, Rhino.Geometry.Mesh):
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(shape)
        elif isinstance(shape, Rhino.Geometry.Brep):
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(shape)
        else:
            Rhino.RhinoApp.WriteLine("Attention: shape is not a mesh or brep: {}".format(type(shape)))
            return

        if not obj_guid:
            Rhino.RhinoApp.WriteLine("Attention: failed to add shape.")
            return

        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
        
        if not obj:
            Rhino.RhinoApp.WriteLine("Attention: failed to find shape.")
            return

        obj.Attributes.LayerIndex = layer_index

        # Plane, object frame and group polyline object.

        attributes = obj.Attributes.Duplicate()
        attributes.SetObjectFrame(Rhino.Geometry.Plane.WorldXY)
        Rhino.RhinoDoc.ActiveDoc.Objects.ModifyAttributes(obj, attributes, False)
        obj.CommitChanges()

        p0 = Rhino.Geometry.Point3d(0, 0, 0)
        p1 = p0 + Rhino.Geometry.Vector3d.XAxis*0.1
        p2 = p0 + Rhino.Geometry.Vector3d.YAxis*0.1
        groupframe = Rhino.Geometry.Polyline([p1, p0, p2])

        groupframe_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddPolyline(groupframe)
        if not groupframe_guid:
            print("Attention: failed to add group frame.")
            return
        groupframe_obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(groupframe_guid)
        if not groupframe_obj:
            print("Attention: failed to find group frame.")
            return
               
        group_index = Rhino.RhinoDoc.ActiveDoc.Groups.Add()
        Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(group_index, obj_guid)
        Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(group_index, groupframe_guid)


        ######################################################################
        # Go through individual attributes and assign the user strings.
        #   name : str = "beam",
        #   index : int = -1,
        #   neighbours : list[int] = [],
        #   features : list[Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh]] = [], 
        #   pair_polyline : list[Rhino.Geometry.Polyline] = [],
        #   pair_polyline_merged : list[Rhino.Geometry.Polyline] = [],
        #   axes : list[Rhino.Geometry.Polyline] = [],
        #   radii : list[list[float]] = [],
        #   thickness : float = 0.0,
        #   insertion : list[Line] = [],
        #   joint_types : list[Rhino.Geometry.TextDot] = [],
        #   joint_volumes : list[list[Rhino.Geometry.Polyline]] = [],
        #   joint_lines : list[Rhino.Geometry.Polyline] = [],
        #   joint_areas : list[Rhino.Geometry.Polyline] = [],
        ######################################################################

        # name
        obj.Attributes.SetUserString("name", name if name else "-")

        # index
        obj.Attributes.SetUserString("index", str(index) if index else "-")

        # neighbours
        obj.Attributes.SetUserString("neighbours", str(neighbours) if neighbours else "-")

        # features - this attribute can be missing when nothing is assigned
        for idx, feature in enumerate(features):
            if isinstance(feature, Rhino.Geometry.Mesh):
                opts = Rhino.FileIO.SerializationOptions()
                opts.WriteUserData = True
                json = feature.ToJSON(opts)
                obj.Attributes.SetUserString(f"feature_{idx}", json)
            elif isinstance(feature, Rhino.Geometry.Brep):
                opts = Rhino.FileIO.SerializationOptions()
                opts.WriteUserData = True
                opts.WriteAnalysisMeshes = False
                opts.WriteRenderMeshes = False
                json = feature.ToJSON(opts)
                obj.Attributes.SetUserString(f"feature_{idx}", json)
        
        # pair_polyline
        list_coordinates = []
        for idx, polyline in enumerate(pair_polyline):
            coordinates = []
            for i in range(polyline.Count):
                coordinates.extend([polyline[i].X, polyline[i].Y, polyline[i].Z])
            list_coordinates.append(coordinates)

        obj.Attributes.SetUserString("pair_polyline", str(list_coordinates) if len(list_coordinates) > 0 else "-")

        # pair_polyline_merged
        list_coordinates = []
        for idx, polyline in enumerate(pair_polyline_merged):
            coordinates = []
            for i in range(polyline.Count):
                coordinates.extend([polyline[i].X, polyline[i].Y, polyline[i].Z])
            list_coordinates.append(coordinates)
        
        obj.Attributes.SetUserString("pair_polyline_merged", str(list_coordinates) if len(list_coordinates) > 0 else "-")

        # axes
        bbox = shape.GetBoundingBox(True)
        str_axes = ""
        if not axes:
            str_axes = "[[0,0,0,0,0,"+ str(bbox.Max.Z-bbox.Min.Z) + "]]"
            axes = [Rhino.Geometry.Polyline([Rhino.Geometry.Point3d(0, 0, 0), Rhino.Geometry.Point3d(0, 0, bbox.Max.Z-bbox.Min.Z)])]
        else:
            axes = []
            for axis in axes:
                numbers = []
                for p in axes:
                    numbers.append(p.X)
                    numbers.append(p.Y)
                    numbers.append(p.Z)
            str_axes = str(axes)

        obj.Attributes.SetUserString("axes", str_axes)

        # radii - per polyline segment
        str_radii = ""
        if len(radii) == 0:
            distance = abs(bbox.Max.X-bbox.Min.X)*0.5
            str_radii = "[[" + str(distance) +"]]"
        else:
            radii_matched_to_axes = []
            count = 0
            for axis in axes:
                numbers = []
                for j in range(len(axis)-1):
                    numbers.append(radii[count%len(radii)])
                    count = count + 1
                radii_matched_to_axes.append(numbers)
            str_radii = str(radii_matched_to_axes)
        obj.Attributes.SetUserString("radii", str_radii)

        # thickness
        obj.Attributes.SetUserString("thickness", str(thickness) if thickness else "-")

        # insertion - this attribute must be handled by a seprate command using closest point search
        obj.Attributes.SetUserString("insertion", "-")
        for line in insertion:
            NotImplementedError("Insertion is not implemented, closest point search is needed.")

        # joints_types - this attribute must be handled by a seprate command using closest point search
        obj.Attributes.SetUserString("joint_types", "-")
        for textdot in joint_types:
            NotImplementedError("Joint types are not implemented, closest point search is needed.")

        # Commit changes and redraw
        obj.CommitChanges()
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()


    def __repr__(self):
        return f"Element"
