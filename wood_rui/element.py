import Rhino
import System
from typing import Union
import ast
from enum import Enum
import wood_rui

class ElementyType(Enum):
    BEAM = "beam"
    PLATE = "plate"

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
        self._index : int = -1  # implemented
        self._neighbours : list[list[int]] = []  # implemented
        self.geometry : Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh] = geometry_plane[0].Geometry  # implemented
        self.elementy_type : str = ElementyType.BEAM  # 0 - plate, 1 beam implemented
        self.index : int = -1 # implemented
        self.plane : Rhino.Geometry.Plane = self._polyline_obj_to_plane(geometry_plane[1]) # implemented
        self.features : Union[list[Rhino.Geometry.Brep], list[Rhino.Geometry.Mesh]] = []  # implemented
        self.insertion : list[Rhino.Geometry.Vector3d] = []  # implemented
        self.axes : list[Rhino.Geometry.Polyline] = []
        self.radii : list[list[float]] = []
        self.thickness : float = 0.0
        self._volumes : list[Rhino.Geometry.Polyline] = []
        self.joints : list[Rhino.Geometry.Polyline] = []  # no need to be implemented, has to be set
        self._user_strings_to_geometry(geometry_plane)

    def _user_strings_to_geometry(self, geometry_plane):
        def process_feature(value, T):
            if value == "-":
                return
            geometry = Rhino.Geometry.GeometryBase.FromJSON(value)
            geometry.Transform(T)
            self.features.append(geometry)
        
        def process_insertion(value, T):
            if value == "-":
                return
            list_of_lists = ast.literal_eval(value)
            for l in list_of_lists:
                my_list = [float(i) for i in l]
                p0 = Rhino.Geometry.Point3d.Origin
                p1 = Rhino.Geometry.Point3d(my_list[0], my_list[1], my_list[2])
                line = Rhino.Geometry.Line(p0, p1)
                line.Transform(T)
                self.insertion.append(line.Direction)

        def process_axes(value, T):
            if value == "-":
                return
            list_of_lists = ast.literal_eval(value)

            for l in list_of_lists:
                my_list = [float(i) for i in l]
                
                polyline = Rhino.Geometry.Polyline()
                for i in range(0, len(my_list), 3):
                    polyline.Add(Rhino.Geometry.Point3d(my_list[i], my_list[i+1], my_list[i+2]))
                polyline.Transform(T)
                self.axes.append(polyline)

        def process_radii(value, T):
            if value == "-":
                return
            list_of_lists = ast.literal_eval(value)
            for l in list_of_lists:
                my_list = [float(i) for i in l]
                self.radii.append(my_list)

        def process_volumes(value, T):
            if value == "-":
                return
            # Add your processing logic here

        def process_thickness(value, T):
            if value == "-":
                return
            # Add your processing logic here

        def process_joints(value, T):
            if value == "-":
                return
            # Add your processing logic here

        # Collect information from user strings
        name_value_collection = geometry_plane[0].Attributes.GetUserStrings()
        string_dictionary = {key: name_value_collection[key] for key in name_value_collection.AllKeys}
        T = Rhino.Geometry.Transform.PlaneToPlane(Rhino.Geometry.Plane.WorldXY, self._polyline_obj_to_plane(geometry_plane[1]))

        # Map keys to processing functions
        key_to_function = {
            "feature": process_feature,
            "insertion" : process_insertion,
            "axes": process_axes,
            "radii": process_radii,
            "volumes": process_volumes,
            "thickness": process_thickness,
            "joints": process_joints,
        }

        for key, value in string_dictionary.items():
            for k, func in key_to_function.items():
                if k in key:
                    func(value, T)

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
                polylines.append(polyline)
            polylines_list.append(polylines)
        
        return polylines_list
    
    @volumes.setter
    def volumes(self, value):
        self._volumes = value

        # Write polylines to user strings
        polylines_coordinates = []
        for i in range(0, len(value), 2):

            polyline_coordinates0 = []
            for j in range(value[i].Count):
                polyline_coordinates0.extend([value[i][j].X, value[i][j].Y, value[i][j].Z])
            
            polyline_coordinates1 = []
            for j in range(value[i+1].Count):
                polyline_coordinates1.extend([value[i+1][j].X, value[i+1][j].Y, value[i+1][j].Z])

            polylines_coordinates.append([polyline_coordinates0, polyline_coordinates1])

        str_volumes = str(polylines_coordinates)

        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(self.geometry_plane[0].Id)
        obj.Attributes.SetUserString("volumes", str_volumes)
        obj.CommitChanges()
    



    @staticmethod
    def get_first_axes(elements):
        return [element.axes[0] for element in elements]

    @staticmethod
    def get_first_radii(elements):
        return [element.radii[0] for element in elements]

    @staticmethod
    def get_first_insertion(elements):
        return [element.insertion for element in elements]

    @staticmethod
    def add_element(
            # layer
            layer_name: str,
            # geometry, plates or beams, use solids.
            geometry: Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh, list[Rhino.Geometry.Polyline]],
            element_type: str,
            # features
            features: list[Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh]], 
            insertion: list[Rhino.Geometry.Line],
            joints_types: list[(str,Rhino.Geometry.Point3d)],
            # simplified geometry
            axes: list[list[Rhino.Geometry.Polyline]],
            radii: list[float], 
            thickness: list[float], 
            # graph
            index: int = -1, 
            neighbours: list[list[int]] = [], 
            # tree
            parent: str = "") -> None:
        """Add a mesh and associated polyline to the specified layer, apply attributes, and group them uniquely.

        Parameters
        ----------
        layer_name : str
            The name of the layer to add the geometry to.
        element_type : str
            The type of the elemen: plate, beam.
        geometry : Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh]
            The geometry to add to the Rhino document.
        features : list[Union[Rhino.Geometry.Brep, Rhino.Geometry.Mesh]]
            The features to add to the Rhino document.
        insertion : list[Rhino.Geometry.Line]
            The insertion lines to add to the Rhino document.
        joints_types : list[(str,Rhino.Geometry.TextDot)]
            The joints types to add to the Rhino document.
        insertion_vectors : list[Rhino.Geometry.Vector3d]
            The insertion vectors to add to the Rhino document.
        axes : list[Rhino.Geometry.Polyline]
            The axes of an element.
        radii : list[float]
            The radius of the axis individual points.
        thickness : list[float]
            The thickness to add to the Rhino document.
        """

        # Create layer or find the existing one.
        layer_index = wood_rui.ensure_layer_exists("compas_wood", "model", layer_name, System.Drawing.Color.Red)
        
        # Add the geometry to the Rhino document.
        if not geometry:
            Rhino.RhinoApp.WriteLine("No geometry to add.")
            return
        
        obj_guid = None

        if isinstance(geometry, Rhino.Geometry.Mesh):
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(geometry)
        elif isinstance(geometry, Rhino.Geometry.Brep):
            obj_guid = Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(geometry)

        if not obj_guid:
            Rhino.RhinoApp.WriteLine("Failed to add geometry.")
            return

        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(obj_guid)
        
        if not obj:
            Rhino.RhinoApp.WriteLine("Failed to find geometry.")
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
            return
        groupframe_obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(groupframe_guid)
        if not groupframe_obj:
            return
        
        # groupframe_obj.Attributes.Visible = False
        # Rhino.RhinoDoc.ActiveDoc.Objects.ModifyAttributes(groupframe_obj, groupframe_obj.Attributes, True)
        
        group_index = Rhino.RhinoDoc.ActiveDoc.Groups.Add()
        Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(group_index, obj_guid)
        Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(group_index, groupframe_guid)

        # Element Type
        obj.Attributes.SetUserString("element_type", element_type)

        # Index
        obj.Attributes.SetUserString("index", str(index))

        # Neighbours
        obj.Attributes.SetUserString("neighbours", str(neighbours) if len(neighbours)>0 else "-")

        # Parent
        obj.Attributes.SetUserString("parent", str(parent) if parent else "-")

        # Features
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


        # Insertion
        str_insertion = ""
        if len(insertion) == 0:
            direction = Rhino.Geometry.Vector3d.XAxis
            str_insertion = "[[" + str(direction.X) + "," + str(direction.Y) + "," + str(direction.Z) + "]]"
        else:
            if element_type == "plate":
                # Plates - Not implemented, must ber per face
                str_insertion = "-"
            elif element_type == "beam":
                # Beams
                directions_matched_to_axes = []
                count = 0
                for axis in axes:
                    numbers = []
                    for j in range(len(axis)-1):
                        numbers.append(insertion[count%len(insertion)].Direction.X)
                        numbers.append(insertion[count%len(insertion)].Direction.Y)
                        numbers.append(insertion[count%len(insertion)].Direction.Z)
                        count = count + 1
                    directions_matched_to_axes.append(numbers)
                str_insertion = str(directions_matched_to_axes)
            else:
                str_insertion = "-"

        obj.Attributes.SetUserString("insertion", str_insertion)
    
        # joints_types
        # TODO: Implement joints types by closest point search        
        str_joint_types = "-"
        if element_type == "beam":
            str_joint_types_list = []
            for joint_type in joints_types:
                try:
                    str_joint_types_list.append(int(joint_type.Text))
                except:
                    print("Joint type must be an integer.")
            str_joint_types = str(str_joint_types_list)
        elif element_type == "plate":
            # Closest point search per object edge
            pass

        obj.Attributes.SetUserString("joint_types", str_joint_types)


        # Axes
        bbox = geometry.GetBoundingBox(True)
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

        # Radius for beams per segment
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

        # Thickness for plates
        text_thickness = "-"
        if not thickness:
            pass
        obj.Attributes.SetUserString("thickness", text_thickness)

        # Thickness for volumes
        text_volumes= "-"
    
        obj.Attributes.SetUserString("volumes", text_volumes)

        # Thickness for volumes
        text_joints= "-"
        obj.Attributes.SetUserString("joints", text_joints)
            
        obj.CommitChanges()

        # Redraw view
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()


    def __repr__(self):
        return (f"Element(\n"
                f"  geometry_plane={self.geometry_plane},\n"
                f"  element_type={self.elementy_type},\n"
                f"  geometry={self.geometry},\n"
                f"  plane={self.plane},\n"
                f"  features={self.features},\n"
                f"  insertion={self.insertion},\n"
                f"  axes={self.axes}, number of axes={len(self.axes)} number of points={self.axes[0].Count},\n"
                f"  radii={self.radii},\n"
                f"  volumes={self.volumes},\n"
                f"  thickness={self.thickness},\n"
                f"  joints={self.joints}\n"
                f")")