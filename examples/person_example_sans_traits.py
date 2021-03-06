""" This example shows the ability to view generic Python objects (not just
HasTraits objects) in HTML using Jigna. The data binding will only be one-way
in this case, i.e. from the UI to the model.
"""

#### Imports ##################################################################

from pyface.qt import QtGui
from jigna.api import View

#### Domain model ####

class Person(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age

#### UI layer ####

body_html = """
  <div>
    Name: <input ng-model="model.name">
    Age: <input ng-model="model.age" type='number'>
  </div>
"""

person_view = View(body_html=body_html)

#### Entry point ####

def main():
    fred = Person(name='Fred', age=42)
    person_view.show(model=fred)

if __name__ == "__main__":
    app = QtGui.QApplication.instance() or QtGui.QApplication([])
    main()
    app.exec_()

#### EOF ######################################################################
