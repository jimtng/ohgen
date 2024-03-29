#!/usr/bin/env python3
# A template based OpenHAB things and items definition generator
# https://github.com/jimtng/openhab-items-generator

import sys
import os
from jinja2 import Environment, FileSystemLoader
import re
import yaml
import argparse

jinja_environment = None
templates = {}
settings = {}
output_buffer = {}
base_path = ""

###############
# Jinja Filters
###############


def quote(value, enclosedby='"'):
    return enclosedby + value.replace(enclosedby, "\\" + enclosedby) + enclosedby if enclosedby and value else value


def csv(items, begin="", end="", enclosedby="", separator=", "):
    if not items:
        return ""

    if type(items) is str:
        return " " + items

    if type(items) is list:
        if enclosedby:
            items = [quote(i, enclosedby) for i in items]

        return begin + separator.join(items) + end

    raise ValueError("The first argument must be a string or a list")


def openhab_groups(items):
    return csv(items, begin=" (", end=")")


def openhab_tags(items):
    return csv(items, begin=" [", end="]", enclosedby='"')


def openhab_metadata(items):
    if type(items) is list:
        for i, item in enumerate(items):
            # print ('type: {}, item: {}'.format(type(item), item))
            if type(item) is not dict:
                continue
            if item.get("key"):
                items[i] = '{}="{}"'.format(item.get("key"), item.get("value"))
                config_list = []
                for config in item.get("configuration"):
                    if type(config) is dict:
                        for key, value in config.items():
                            if value in ["true", "false"]:
                                config_list.append("{}={}".format(key, value))
                            else:
                                config_list.append('{}="{}"'.format(key, value))
                    else:
                        config_list.append(str(config))
                items[i] += " [ {} ]".format(csv(config_list))
            else:
                item_list = []
                for key, value in item.items():
                    item_list.append('{}="{}"'.format(key, value))
                items[i] = csv(item_list)

    return csv(items, begin=", ")


def warn(msg):
    print("# [WARNING] " + msg)


# From http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        try:
            choice = input().lower()
        except KeyboardInterrupt:
            print()
            sys.exit()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


# load template from file into the templates dict if not already loaded
def load_template(template_name):
    global templates
    if template_name in templates:
        return

    things_template = ""
    items_template = ""

    things_nest_level = 0

    # Is the template file specified?
    try:
        template_file_name = settings["templates"][template_name]["template-file"]
    except:
        template_file_name = "templates/{}.tpl".format(template_name)

    template_file_name = os.path.join(base_path, template_file_name)

    with open(template_file_name) as template_file:
        for line in template_file:
            line_stripped = line.strip()
            if line_stripped == "":
                continue

            if line_stripped.startswith("Thing ") or line_stripped.startswith("Bridge "):
                if things_template != "":
                    things_template += "\n"
                things_template += line
                if line_stripped.endswith("{"):
                    things_nest_level += 1
                continue

            if things_nest_level > 0:
                things_template += line
                if line_stripped.startswith("}"):
                    things_nest_level -= 1
                continue

            items_template += line

    try:
        templates[template_name] = {
            "filename": template_file_name,  # to derive its path
            "things": jinja_environment.from_string(things_template),
            "items": jinja_environment.from_string(items_template)
            # 'things': things_template,
            # 'items': items_template
        }
    except Exception as e:
        warn('Failed loading template "{}": {}'.format(template_name, str(e)))


def split_camel_case(str):
    return " ".join(re.findall(r"[A-Z0-9](?:[a-z0-9]+|[A-Z]*(?=[A-Z]|$))", str))


def get_template_name(thing):
    return thing.get("template", settings.get("template"))


def generate(name, thing):
    template_name = get_template_name(thing)
    if not template_name:
        warn("{} has no template, and no default template has been specified".format(name))
        return

    try:
        load_template(template_name)
    except FileNotFoundError as err:
        warn("Error loading the template for '{}', template: '{}' {}".format(name, template_name, err))
        return

    generated = {}
    for part in ["things", "items"]:
        try:
            generated[part] = templates[template_name][part].render(thing)
        except:
            warn(
                "Template error. Thing: '{}' Template: '{}' Error: {}".format(
                    thing["name"], template_name, sys.exc_info()[1]
                )
            )
            return None

    return generated


def get_output_file(output_name, section):
    return settings.get("outputs", {}).get(output_name, {}).get(section)


def add_thing_to_buffer(thing, things_data, items_data):
    global output_buffer
    template_name = get_template_name(thing)
    if not template_name:
        return

    output_name = (
        thing.get("output", None)
        or settings.get("templates", {}).get(template_name, {}).get("output", None)
        or settings.get("output", None)
    )

    if not output_name:
        warn("{}: No output name".format(thing["name"]))
        return

    things_file = get_output_file(output_name, "things-file")
    items_file = get_output_file(output_name, "items-file")

    if not things_file:
        warn("{}: missing things-file output setting".format(thing["name"]))
        return
    if not items_file:
        warn("{}: missing items-file output setting".format(thing["name"]))
        return

    if output_name not in output_buffer:
        output_buffer[output_name] = {}
    output_buffer[output_name].setdefault("things-file", []).append(things_data)
    output_buffer[output_name].setdefault("items-file", []).append(items_data)


def save_output_buffer(overwrite=False):
    # write output
    for output_name in output_buffer:
        for part in output_buffer[output_name]:
            file_name = get_output_file(output_name, part)
            file_name = os.path.join(base_path, file_name)
            headers = part + "-header"
            footers = part + "-footer"
            if os.path.isfile(file_name):
                if not overwrite and not query_yes_no(
                    "File '{}' exists. Overwrite?".format(os.path.abspath(file_name))
                ):
                    continue
                status = "updated"
            else:
                status = "created"
            with open(file_name, "w") as file:
                # write global headers
                if "header" in settings:
                    file.write(settings["header"])

                # write output specific headers
                if headers in settings["outputs"][output_name]:
                    file.write(settings["outputs"][output_name][headers])

                # write the generated content
                file.write("\n\n".join(output_buffer[output_name][part]))

                # write output specific footers
                if footers in settings["outputs"][output_name]:
                    file.write(settings["outputs"][output_name][footers])

                # write global footers
                if "footer" in settings:
                    file.write(settings["footer"])

            print("{} - {}".format(file_name, status))


def main():
    global settings, jinja_environment

    parser = argparse.ArgumentParser(description="OpenHAB Things and Items Generator")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite output files without prompting")
    parser.add_argument(
        "input",
        nargs="?",
        default="devices.yaml",
        help='A file containing the list of things/items to generate. If not specified, a file called "device.yaml" will be loaded',
    )
    options = parser.parse_args()

    devices_file_name = options.input
    base_path = os.path.dirname(devices_file_name)
    try:
        with open(devices_file_name) as f:
            data = yaml.load(f.read(), Loader=yaml.BaseLoader)
    except:
        warn("{}".format(sys.exc_info()[1]))
        sys.exit()

    if not data:
        warn("No data found in {}".format(devices_file_name))
        sys.exit()

    settings = data.pop("settings", {})

    # load jinja environment, set the loader path to dir(devices_file_name) + /templates
    jinja_environment = Environment(loader=FileSystemLoader(os.path.join(base_path, "templates")))
    jinja_environment.filters.update(
        {
            "csv": csv,
            "groups": openhab_groups,
            "tags": openhab_tags,
            "metadata": openhab_metadata,
            "quote": quote,
            "to_label": split_camel_case,
        }
    )

    # load all the yaml data first and generate each thing
    for name, thing in data.items():
        thing.setdefault("name", name)
        # fill in some useful variables
        thing.setdefault("label", split_camel_case(name.replace("_", " ")))
        thing.setdefault("thingid", name.replace("_", "-").lower())
        thing.setdefault("name_parts", name.split("_"))
        thing.setdefault("room", split_camel_case(name.split("_")[0]))

        output = generate(name, thing)
        if output:
            add_thing_to_buffer(thing, output["things"], output["items"])

    save_output_buffer(options.overwrite)

    print("Devices: {}".format(len(data)))


if __name__ == "__main__":
    main()
