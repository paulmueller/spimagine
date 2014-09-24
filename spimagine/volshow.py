import sys
import numpy as np

from PyQt4 import QtCore,QtGui

from collections import OrderedDict
from spimagine.gui_mainwindow import MainWindow

from spimagine.data_model import DataModel, GenericData, EmptyData, DemoData, NumpyData

_MAIN_APP = None

#FIXME app issue

def getCurrentApp():
    app = QtGui.QApplication.instance()

    if not app:
        app = QtGui.QApplication(sys.argv)

    if not hasattr(app,"volfigs"):
        app.volfigs = OrderedDict()

    global _MAIN_APP
    _MAIN_APP = app
    return _MAIN_APP



def volfig(num=None):
    """return window"""

    app = getCurrentApp()
    #filter the dict
    app.volfigs =  OrderedDict((n,w) for n,w in app.volfigs.iteritems() if w.isVisible())

    if not num:
        if len(app.volfigs.keys())==0:
            num = 1
        else:
            num = max(app.volfigs.iterkeys())+1

    if app.volfigs.has_key(num):
        window = app.volfigs[num]
        app.volfigs.pop(num)
    else:
        window = MainWindow(dataContainer=EmptyData())
        window.show()

    #make num the last window
    app.volfigs[num] = window
    window.raise_()
    return window


def volshow(data, scale = True, stackUnits = [.1,.1,.1], blocking = False ):
    """
    class to visualize 3d/4d data

    data can be

    - a 3d/4d numpy array of dimensions (z,y,x) or (t,z,y,x)

      e.g.

         volshow( randint(0,10,(10, 20,30,40) )



    - an instance of a class derived from the abstract bass class GenericData

      e.g.

        from spimagine.data_model import GenericData

        class myData(GenericData):
            def __getitem__(self,i):
                return (100*i+3)*ones((100,100,100)
            def size(self):
                return (4,100,100,100)

        volshow(myData())

        or
        from spimagine.data_model import DataModel

        volshow(DataModel(dataContainer=myData(), prefetchSize= 5)



    returns window.glWidget if not in blocking mode """


    app = getCurrentApp()

    # check whether there are already open windows, if not create one
    try:
        num,window = [(n,w) for n,w in app.volfigs.iteritems()][-1]
    except:
        num = 1

    window = volfig(num)



    if isinstance(data,GenericData):
        m = DataModel(data)
    elif isinstance(data,DataModel):
        m = data
    else:
        if scale:
            ma,mi = np.amax(data), np.amin(data)
            if ma==mi:
                ma +=1.
            data = 16000.*(data-mi)/(ma-mi)

        m = DataModel(NumpyData(data.astype(np.float32)))

    # m = NumpyData(data.astype(np.float32))
    # window = MainWindow(dataContainer = m)

    window.setModel(m)

    if blocking:
        getCurrentApp().exec_()
    else:
        return window.mainWidget.glWidget


if __name__ == '__main__':

    N = 256
    # d = np.linspace(0,100,N**3).reshape((N,)*3)
    d = np.zeros((100,)*3,dtype=np.float32)
    d[50,:,:] = 1.


    class myData(GenericData):
        def __getitem__(self,i):
            return (100*i+3)*d
        def size(self):
            return (4,)+d.shape



    volshow(myData(), blocking = True)

    # volshow(d, blocking = True)
