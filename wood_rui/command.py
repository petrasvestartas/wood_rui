import Rhino
import typing
from typing import *
import wood_rui


def handle_string_input(option_name: str) -> str:
    """Get string from user input."""
    go = Rhino.Input.Custom.GetString()
    go.SetCommandPrompt(f"Enter value for {option_name}")

    if go.Get() != Rhino.Input.GetResult.String:
        Rhino.RhinoApp.WriteLine("Nothing is selected, returning to main menu.")
        return None

    return go.StringResult()


def handle_numbers_input(option_name: str) -> list[float]:
    """Get numbers from user input."""
    go = Rhino.Input.Custom.GetString()
    go.SetCommandPrompt(f"Enter {option_name} as comma-separated values (e.g., 0.0, 1.0, 2.5)")

    if go.Get() != Rhino.Input.GetResult.String:
        Rhino.RhinoApp.WriteLine("Nothing is selected, returning to main menu.")
        return []

    input_str = go.StringResult()
    try:
        return [float(val.strip()) for val in input_str.split(",")]
    except ValueError:
        Rhino.RhinoApp.WriteLine("Invalid input. Please enter valid numbers separated by commas.")
        return []


def handle_integers_input(option_name: str) -> list[int]:
    """Get integers from user input."""
    go = Rhino.Input.Custom.GetString()
    go.SetCommandPrompt(f"Enter {option_name} as comma-separated integers (e.g., 1, 2, 3)")

    if go.Get() != Rhino.Input.GetResult.String:
        Rhino.RhinoApp.WriteLine("Nothing is selected, returning to main menu.")
        return []

    input_str = go.StringResult()
    try:
        return [int(val.strip()) for val in input_str.split(",")]
    except ValueError:
        Rhino.RhinoApp.WriteLine("Invalid input. Please enter valid integers separated by commas.")
        return []


def handle_polylines_input(option_name: str, hide : bool = True) -> list[Rhino.Geometry.Polyline]:
    """Select polylines from Rhino document."""
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt(f"Select {option_name}")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve  # Filter to curves
    go.EnablePreSelect(True, True)
    go.SubObjectSelect = False
    go.DeselectAllBeforePostSelect = False
    res = go.GetMultiple(1, 0)


    polylines = []  
    if go.CommandResult() == Rhino.Commands.Result.Success:
        selected_curves = [go.Object(i).Curve() for i in range(go.ObjectCount) if go.Object(i).Curve()]
        
        for curve in selected_curves:
            result, polyline = curve.TryGetPolyline()
            if result:
                polylines.append(polyline)
            else:
                Rhino.RhinoApp.WriteLine("One of the selected curves could not be converted to a polyline.")
        
    return polylines


def handle_lines_input(option_name: str, hide : bool = True) -> list[Rhino.Geometry.Line]:
    """Select lines from Rhino document."""
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt(f"Select {option_name}")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve  # Filter to curves
    go.EnablePreSelect(True, True)
    go.SubObjectSelect = False
    go.DeselectAllBeforePostSelect = False
    res = go.GetMultiple(1, 0)

    lines = []
    if go.CommandResult() == Rhino.Commands.Result.Success:
        selected_curves = [go.Object(i).Curve() for i in range(go.ObjectCount) if go.Object(i).Curve()]
        lines = [Rhino.Geometry.Line(c.PointAtStart, c.PointAtEnd) for c in selected_curves]
        
    return lines


def handle_mesh_input(option_name: str, hide: bool = True) -> list[Rhino.Geometry.Mesh]:
    """Select Meshes from Rhino document."""
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt(f"Select {option_name}")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Mesh  # Filter to meshes
    go.EnablePreSelect(True, True)
    go.SubObjectSelect = False
    go.DeselectAllBeforePostSelect = False
    res = go.GetMultiple(1, 0)

    selected_meshes = []
    if go.CommandResult() == Rhino.Commands.Result.Success:
        
        for i in range(go.ObjectCount):
            rhino_obj = go.Object(i).Object()  # Get the RhinoObject
            
            if hide:
                Rhino.RhinoDoc.ActiveDoc.Objects.Hide(rhino_obj.Id, True)
            
            if rhino_obj and rhino_obj.Geometry and isinstance(rhino_obj.Geometry, Rhino.Geometry.Mesh):
                selected_meshes.append(rhino_obj.Geometry)
        
        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()  # Refresh view after hiding objects
        

    return selected_meshes


def handle_brep_input(option_name: str, hide : bool = True) -> list[Rhino.Geometry.Brep]:
    """Select Breps from Rhino document."""
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt(f"Select {option_name}")
    go.GeometryFilter =Rhino.DocObjects.ObjectType.Surface | Rhino.DocObjects.ObjectType.PolysrfFilter # Filter to curves
    go.EnablePreSelect(True, True)
    go.SubObjectSelect = False
    go.DeselectAllBeforePostSelect = False
    res = go.GetMultiple(1, 0)

    selected_breps = []

    if go.CommandResult() == Rhino.Commands.Result.Success:
        for i in range(go.ObjectCount):
            obj_ref = go.Object(i)
            if hide:
                Rhino.RhinoDoc.ActiveDoc.Objects.Hide(obj_ref, False)
            selected_breps.append(obj_ref.Brep())
    return selected_breps


def handle_solid_input(option_name: str, hide: bool = True) -> Tuple[list[Rhino.Geometry.Brep], list[Rhino.Geometry.Mesh]]:
    """Select Breps and Meshes from Rhino document."""

    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt(f"Select {option_name}")
    Rhino.DocObjects.ObjectType.Surface | Rhino.DocObjects.ObjectType.PolysrfFilter | Rhino.DocObjects.ObjectType.Mesh  # Filter to Breps and Meshes
    go.EnablePreSelect(True, True)
    go.SubObjectSelect = False
    go.DeselectAllBeforePostSelect = False
    res = go.GetMultiple(1, 0)

    selected_breps = []
    selected_meshes = []
    if go.CommandResult() == Rhino.Commands.Result.Success:

        for i in range(go.ObjectCount):
            rhino_obj = go.Object(i)  # Get the RhinoObject

            if hide:
                Rhino.RhinoDoc.ActiveDoc.Objects.Hide(rhino_obj.Id, True)

            if rhino_obj:
                if isinstance(rhino_obj.Object().Geometry, Rhino.Geometry.Mesh):
                    selected_breps.append(rhino_obj.Geometry)
                else:
                    selected_breps.append(rhino_obj.ToBrep())

        Rhino.RhinoDoc.ActiveDoc.Views.Redraw()  # Refresh view after hiding objects

    return selected_breps, selected_meshes


# Main method that 
def generalized_input_method(
    
    dataset_name: str,
    input_dict: Dict[
        str,
        Tuple[
            Union[float, int, list[float], list[int], list[Rhino.Geometry.Line], list[Rhino.Geometry.Polyline], list[Rhino.Geometry.Mesh], list[Rhino.Geometry.Brep]], type
        ],
    
    ],
    callback=None,
    run_when_input_changed=True,
    hide_input = False
) -> None:
    """Processes input types based on the input dictionary."""
    get_options = Rhino.Input.Custom.GetOption()

    # Dynamically add options based on the input dictionary
    dict_options = {}
    dict_values = {}

    for option_name, (default_value, value_type) in input_dict.items():

        # print(option_name, value_type)
        if value_type is float:
            print(option_name, "float")
            dict_options[option_name] = Rhino.Input.Custom.OptionDouble(default_value)  # float
            dict_values[option_name] = dict_options[option_name].CurrentValue
            get_options.AddOptionDouble(option_name, dict_options[option_name])
        elif value_type is int:
            print(option_name, "int")
            dict_options[option_name] = Rhino.Input.Custom.OptionInteger(default_value)  # int
            dict_values[option_name] = dict_options[option_name].CurrentValue
            get_options.AddOptionInteger(option_name, dict_options[option_name])
        elif value_type is bool:
            print(option_name, "bool")
            dict_options[option_name] = Rhino.Input.Custom.OptionToggle(default_value, "Yes", "No")
            dict_values[option_name] = dict_options[option_name].CurrentValue
            get_options.AddOptionToggle(option_name, dict_options[option_name])
        elif value_type is typing.List[float]:  # List of floats
            print(option_name, "list float")
            get_options.AddOption(option_name)
        elif value_type is typing.List[int]:  # List of ints
            print(option_name, "list int")
            get_options.AddOption(option_name)
        elif value_type is typing.List[Rhino.Geometry.Line]:  # List of lines
            print(option_name, "list line")
            get_options.AddOption(option_name)
        elif value_type is typing.List[Rhino.Geometry.Polyline]:  # List of polylines
            print(option_name, "list polyline")
            get_options.AddOption(option_name)
        elif value_type is typing.List[Rhino.Geometry.Mesh]:  # List of polylines
            print(option_name, "list mesh")
            get_options.AddOption(option_name)
        elif value_type is typing.List[Rhino.Geometry.Brep]:  # List of polylines
            print(option_name, "list brep")
            get_options.AddOption(option_name)
        elif value_type is typing.List[wood_rui.Group]:  # List of polylines
            print(option_name, "list group")
            get_options.AddOption(option_name)
        elif value_type is Callable:
            print(option_name, "Callable")
            get_options.AddOption(option_name)

    # Run external method to update geometry each time the input is changed.
    callback(input_dict, dataset_name)

    # Command prompt
    get_options.SetCommandPrompt("Select input method and options.")

    done = False
    while not done:
        # Get the result from the option dialog
        res = get_options.Get()

        # If an option is selected
        if res == Rhino.Input.GetResult.Option:
            option_name = get_options.Option().EnglishName
            input_type = input_dict[option_name][1]

            if input_type is float or input_type is int or input_type is bool:
                input_dict[option_name] = (dict_options[option_name].CurrentValue, input_type)
                print("input_dict[option_name]", dict_options[option_name].CurrentValue)
            elif input_type is typing.List[float]:
                result = handle_numbers_input(option_name, hide_input)
                if result:
                    input_dict[option_name] = (result, input_type)
                    Rhino.RhinoApp.WriteLine(f"Selected numbers for {option_name}: {result}")
            elif input_type is typing.List[int]:
                result = handle_numbers_input(option_name, hide_input)
                if result:
                    input_dict[option_name] = (result, input_type)
                    Rhino.RhinoApp.WriteLine(f"Selected integers for {option_name}: {result}")
            elif input_type is typing.List[Rhino.Geometry.Line]:  # List of Line
                result = handle_lines_input(option_name, hide_input)
                if result:
                    input_dict[option_name] = (result, input_type)
                    Rhino.RhinoApp.WriteLine(f"Selected lines for {option_name}: {len(result)} lines selected.")
            elif input_type is typing.List[Rhino.Geometry.Polyline]:  # List of Polyline
                result = handle_polylines_input(option_name, hide_input)
                if result:
                    input_dict[option_name] = (result, input_type)
                    Rhino.RhinoApp.WriteLine(f"Selected lines for {option_name}: {len(result)} polylines selected.")
            elif input_type is typing.List[Rhino.Geometry.Mesh]:  # List of Mesh
                result = handle_mesh_input(option_name, hide_input)
                if result:
                    input_dict[option_name] = (result, input_type)
                    Rhino.RhinoApp.WriteLine(f"Selected lines for {option_name}: {len(result)} meshes selected.")
            elif input_type is typing.List[Rhino.Geometry.Brep]:  # List of Mesh
                result = handle_brep_input(option_name, hide_input)
                if result:
                    input_dict[option_name] = (result, input_type)
                    Rhino.RhinoApp.WriteLine(f"Selected lines for {option_name}: {len(result)} breps selected.")
            elif input_type is typing.List[wood_rui.Group]:  # List of Group
                result = wood_rui.select_and_find_valid_groups("Groups")  # geometry_planes
                if result:
                    input_dict[option_name] = (result, input_type)
                    Rhino.RhinoApp.WriteLine(f"Selected lines for {option_name}: {len(result)} groups selected.")
            elif input_type is typing.Callable:  # External Function
                print(input_dict[option_name])
                input_dict[option_name][0]()
                Rhino.RhinoApp.WriteLine(f"External function is called {option_name}.")

            # Run external method to update geometry each time the input is changed.
            if run_when_input_changed:
                callback(input_dict, dataset_name)

        elif res == Rhino.Input.GetResult.Nothing or res == Rhino.Input.GetResult.Cancel:
            Rhino.RhinoApp.WriteLine("No option selected or operation canceled. Exiting...")
            done = True  # Exit the loop by setting done to True
        
    if not run_when_input_changed:
        callback(input_dict, dataset_name)

    # Final output and return success
    return Rhino.Commands.Result.Success
