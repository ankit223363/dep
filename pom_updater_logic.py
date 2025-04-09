import os
from lxml import etree as ET

def update_versions_in_project(project_dir, backend_data, module_data, preview=False):
    changes_log = []

    def find_version_in_tag(tag_text):
        for entry in backend_data + module_data:
            if entry['module'] in tag_text:
                return entry['version']
        return None

    for root_dir, _, files in os.walk(project_dir):
        for file in files:
            if file == "pom.xml":
                pom_path = os.path.join(root_dir, file)
                parser = ET.XMLParser(remove_blank_text=False)
                tree = ET.parse(pom_path, parser)
                root = tree.getroot()
                ns = {'ns': 'http://maven.apache.org/POM/4.0.0'}
                props = root.find('ns:properties', ns)
                if props is None:
                    continue

                updated = False
                changes = []

                for elem in props:
                    if not hasattr(elem, 'tag') or not isinstance(elem.tag, str):
                        continue
                    tag = elem.tag.split('}', 1)[-1]
                    if tag.endswith('.version'):
                        new_version = find_version_in_tag(tag)
                        if new_version and elem.text != new_version:
                            changes.append(f"{tag}: {elem.text} -> {new_version}")
                            if not preview:
                                elem.text = new_version
                            updated = True

                if updated:
                    if not preview:
                        xml_content = ET.tostring(root, pretty_print=True, encoding='UTF-8').decode('utf-8')
                        with open(pom_path, 'w', encoding='utf-8') as f:
                            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                            f.write(xml_content)

                    changes_log.append({
                        "file": pom_path,
                        "changes": changes
                    })

    return changes_log