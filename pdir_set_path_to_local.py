# Switch  from PDIR to real paths
import os
import ix



def get_root():
    # get root path of the loaded project file
    head, tail = os.path.split(ix.application.get_current_project_filename())
    return head


def get_references():
    # gets all referenced contexts
    referenced_contexts = []
    contexts = ix.api.OfContextSet()
    ix.application.get_factory().get_root().resolve_all_contexts(contexts)
    for context in contexts:
        if context.is_reference():
            referenced_contexts.append(str(context))

    return referenced_contexts


def gather_all_filenames():
    # gathers all objects/ project item class to a list
    # gets all items - enabled and disabled

    all_files = []
    class_names = ix.api.CoreStringArray(1)
    class_names[0] = "ProjectItem"

    empty_mask = ix.api.CoreBitFieldHelper()

    all_objects = ix.api.OfObjectArray()
    root_context = ix.application.get_factory().get_root()
    root_context.get_all_objects(class_names, all_objects, empty_mask)


    for f in all_objects:
        if not ix.get_item(str(f.get_parent_item())).is_reference():
            try:
                if f.attrs.filename:
                    check_file = f.get_attribute("filename")
                    if f.attrs.filename != "":
                        all_files.append(f)
            except:
                pass

    return all_files


def check_if_pdir(item_path=None):
    # check if pdir in path
    if "$pdir" in item_path.lower():
        return True
    else:
        return False


def check_if_pdir_match(item_path=None, source_path=get_root()):
    # check if already a pdired item
    if str(source_path) in str(item_path):
        return True


def check_if_exists(pathobject):
    # checks if path already exists either as a directory or filename
    if os.path.isfile(pathobject):
        return True
    else:
        return False


def swap_paths(itemobject, newpath):
    # replace paths to the object with the new paths

    at = itemobject.get_attribute("filename")
    if at.is_locked():
        print("Attribute locked on {}".format(str(itemobject)))
        ix.cmds.LockAttributes([str(itemobject) + "." + at.get_name()], False)
        ix.application.check_for_events()
    if itemobject.get_attribute("filename").get_raw_string().split(".")[-1] in ["usd", "abc"]:
        print "change reference path"

    at.set_string(str(newpath))
    ix.application.check_for_events()


def get_raw_item_filename(itemobject):
    # read a raw string for the object
    # takes clarisse object
    return itemobject.get_attribute("filename").get_raw_string()


def cleanup_string(input_string):
    # there could be a mix of character separators, so we want to
    # clean those up first
    cleanup_string = os.path.normpath(input_string)
    return cleanup_string


def rundown(mode=None):
    project_root = cleanup_string(get_root())
    print("   ")
    print("-------------------------------")
    print("Running Path replacer for PDIR")
    print("Local project path {}".format(project_root))
    print(" ")

    all_files = gather_all_filenames()
    all_references = get_references()

    print("Found: {} ProjectItems".format(str(len(all_files+all_references))))

    print("References:")
    for ref in all_references:
        print
        print("    Object Referenced item: {}".format(str(ix.item_exists(str(ref)))))


    print("   ")
    print("Files:")
    for found_filename_object in all_files+all_references:
        found_filename_object = ix.item_exists(str(found_filename_object))

        print("    Object item: {}".format(str(found_filename_object)))

        item_path = get_raw_item_filename(found_filename_object)
        cleaned_path = cleanup_string(item_path)
        print("    Object path: {}".format(cleaned_path))

        if "pdir" in mode:
            if not check_if_pdir(item_path=cleaned_path):
                print("    No $PDIR in {}".format(cleaned_path))
                if check_if_pdir_match(item_path=cleaned_path, source_path=project_root):
                    new_path = cleaned_path.replace(project_root, "$PDIR")
                    swap_paths(found_filename_object, new_path)
                    print("    - Path changed to $PDIR")

            else:
                print("    Path already PDIR {}".format(cleaned_path))

        if "local" in mode:
            if check_if_pdir(item_path=cleaned_path):
                print("    Found $PDIR in {}".format(cleaned_path))
                new_path = cleaned_path.replace("$PDIR", project_root)
                swap_paths(found_filename_object, new_path)
                print("    - Path changed to Local path")
    ix.application.check_for_events()

    print(" ")
    print("-------- Done. ------------- ")



if __name__ == "__main__":

    #rundown(mode="pdir")
    rundown(mode="local")