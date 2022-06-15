from pathlib import Path
from typing import List
from xml.dom import minidom
from xml.etree import ElementTree


class Project:
    """
    Represents a Pyssembler project
    """
    def __init__(self, project_file: Path, main: Path, files: List[Path] = None,
                 exception_handler: Path = None):
        self._project_file = project_file
        self._root: Path = self._project_file.parent
        self._files: List[Path] = files or []
        self._main: Path = main
        self._exception_handler: Path = exception_handler

    @classmethod
    def parse(cls, project_file: Path):
        xml = ElementTree.parse(project_file)
        root = xml.getroot()
        main = None
        files = []
        eh = None
        for child in root:
            if child.tag == 'main':
                main = Path(child.attrib['name']).resolve()
            elif child.tag == 'file':
                files.append(Path(child.attrib['name']).resolve())
            elif child.tag == 'exception_handler':
                eh = Path(child.attrib['name']).resolve()
        return cls(project_file, main, files, eh)

    @property
    def root(self):
        return self._root

    def save(self):
        xml_root = minidom.Document()
        project = xml_root.createElement('project')
        main = project.proj.createElement('main')
        main.setAttribute('name', str(self._main))
        for file in self._files:
            f = project.createElement('file')
            f.setAttribute('name', file)
        eh = project.createElement(str('exception_handler'))
        if self._exception_handler:
            eh.setAttribute('name', str(self._exception_handler))
        xml_str = xml_root.toprettyxml(indent='\t')
        with self._project_file.open('w') as f:
            f.write(xml_str)

