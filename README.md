[![Build Status](https://travis-ci.org/openworm/PyOpenWorm.png?branch=alpha0.5-slarson)](https://travis-ci.org/openworm/PyOpenWorm)

PyOpenWorm
===========

A unified, simple data access library for data & facts about *C. elegans* biology

What does it do?
----------------

Enables a simple API for asking various questions about the cells of the *C. elegans*, enabling the sharing of data about *C. elegans* for the purpose of building a data-to-model pipeline for the OpenWorm project.

Installation
------------

See INSTALL.md

Basic Usage
-----------

To get started, you'll probably want to load in the database. If you cloned the repository from Github, then the database will be in the OpenWormData subdirectory. You can read it in
by doing 

```python
  >>> import PyOpenWorm as P
  >>> P.connect()

  >>> P.loadData()
  [PyOpenWorm] Loading data into the graph; this may take several minutes!!


```

Then you can try out a few things:

```python

  # Grabs the representation of the neuronal network
  >>> net = P.Worm().get_neuron_network()
  
  # Grab a specific neuron
  >>> aval = net.aneuron('AVAL')
  
  >>> aval.type()
  set(['interneuron'])

  #show how many connections go out of AVAL
  >>> aval.connection.count('pre')
  77

```

Why is this necessary?
----------------------

There are many different useful ways to compute with data related to the worm.
Different data structures have different strengths and answer different questions.
For example, a NetworkX representation of the connectome as a complex graph enables
questions to be asked about first and second nearest neighbors of a given neuron.
In contrast, an RDF semantic graph representation is useful for reading and 
writing annotations about multiple aspects of a neuron, such as what papers 
have been written about it, multiple different properties it may have such as
ion channels and neurotransmitter receptors.  A NeuroML representation is useful
for answering questions about model morphology and simulation parameters.  Lastly,
a Blender representation is a full 3D shape definition that can be used for 
calculations in 3D space.  Further representations regarding activity patterns
such as Neo or simulated activity can be considered as well.

Using these different representations separately leads to ad hoc scripting for
for each representation.  This presents a challenge for data integration and 
consolidation of information in 'master' authoritative representations.  By
creating a unified data access layer, different representations
can become encapsulated into an abstract view.  This allows the user to work with
objects related to the biological reality of the worm.  This has the advantage that 
the user can forget about which representation is being used under the hood.  

The worm itself has a unified sense of neurons, networks, muscles,
ion channels, etc and so should our code.
  
More examples
-------------
  
Returns information about individual neurons::

```python
  >>> aval.name()
  'AVAL'

  #list all known receptors
  >>> aval.receptors()
  set(['GLR-1', 'NMR-1', 'GLR-4', 'GLR-2', 'GGR-3', 'UNC-8', 'GLR-5', 'NMR-2'])

  #show how many chemical synapses go in and out of AVAL
  >>> aval.Syn_degree()
  74

```

Returns the list of all neurons::

```python
  #NOTE: This is a VERY slow operation right now
  >>> len(set(net.neurons()))
  302
  >>> set(net.neurons())
  set(['VB4', 'PDEL', 'HSNL', 'SIBDR', ... 'RIAL', 'MCR', 'LUAL'])

```

Returns a set of all muscles::

```python
  >>> P.Worm().muscles()
  set([MANAL, MDL23, MVR02, ... MVL09, MVR21, MDR03])

```

See what some evidence stated::
```python
  >>> e0 = P.Evidence(author='Sulston et al.', date='1983')
  >>> list(e0.asserts())
  [Neuron(name=AVDL,lineageName=AB alaaapalr)]

```

For most types (i.e., subclasses of `P.DataObject`) that don not have required
initialization arguments, you can load all members of that type by making an
object of that type and calling `load()`::
```python
  >>> list(P.Neuron().load())
  [AS6,SIBVL,AS5,AVKL,VD10,VA5,AVG,AUAR,AWAR,PLML,...]

```

See what neurons express some neuropeptide::
```python
  >>> n = P.Neuron()
  >>> n.neuropeptide("TH")
  neuropeptide=TH

  >>> s = set(x.name() for x in n.load()) 
  >>> s == set(['CEPDR', 'PDER', 'CEPDL', 'PDEL', 'CEPVR', 'CEPVL'])
  True

```

See what neurons innervate a muscle::
```python
   >>> muscles = P.Worm().muscles()
   >>> a_muscle = muscles.pop()
   >>> a_muscle
   MRV17
   >>> a_muscle.innervatedBy()
   set([VB8, VD10, VB9, VD9, VA10])

```
Get direct access to the RDFLib graph::
```python
 >>> P.config('rdf.graph').query("SELECT ?y WHERE { ?x rdf:type ?y }")

```

Returns the c. elegans connectome represented as a [NetworkX](http://networkx.github.io/documentation/latest/) graph::

```python
  >>> net.as_networkx()
  <networkx.classes.digraph.DiGraph object at 0x10f28bc10>

```

More examples can be found [here](http://pyopenworm.readthedocs.org/en/alpha0.5/making_dataObjects.html) and [here](https://github.com/openworm/PyOpenWorm/tree/alpha0.5/examples).


Ease of use
-----------

This library should be easy to use and easy to install, to make it most accessible.  Python beginners should be able to get information out about c. elegans from this library.  Sytactical constructs in this library should be intuitive and easy to understand what they will return within the knowledge domain of c. elegans, 
rather than in the programming domain of its underlying technologies.  Values that are returned should be easily interpretable and easy to read.
Wherever possible, pure-python libraries or those with few compilation requirements, rather than those that create extra dependencies on external native libraries are used.

Versioning data as code
-----------------------
As the underlying data sets that define the c. elegans anatomy change over time, these 
changes can often break a library that attempts to reliably expose those data.  This is 
because data changes can cause queries to return different answers than before, causing
unit tests that rely on those answers to no longer correctly return.  As such, to create
a stable foundational library for others to reuse, the version of the PyOpenWorm library 
guarantees the user a specific version of the data behind that library.  As data
are improved, the maintainers of the library can perform appropriate regression tests
prior to each new release to guarantee stability.

