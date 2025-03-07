NOTICE
======
This product includes software developed at "West University of Timisoara, Romania", as part of the 
"SCAMP-ML - Statistici computaționale avansate pentru planificarea și urmărirea mediilor de producție" 
(Organismul Intermediar pentru Cercetare (OIC) - Program Operațional Competitivitate, Componenta 1 – Proiect
Tehnologic Inovativ pentru regiuni mai puțin dezvoltate (fără București – Ilfov), axa prioritară - Cercetare, 
dezvoltare tehnologică și inovare (CDI)).

DEVELOPERS
==========
Flavia Micota flavia.micota@e-uvt.ro
Adrian Copie adrian.copie@e-uvt.ro
Theodora Grumeza theodor.grumeza@e-uvt.ro
Octavian Maghiar octavian.maghiar98@e-uvt.ro
Mircea Marin mircea.marin@e-uvt.ro
Teodora Selea teodora.selea@e-uvt.ro
Daniela Zaharie daniela.zaharie@e-uvt.ro

COPYRIGHT
=========
Copyright 2021-2023, West University of Timișoara, Timișoara, Romania
    https://www.uvt.ro/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



PLEASE DO NOT DELETE THIS FILE!!
===============================

This data generator can be utilized to generate data that could be further be used by various planification algorithms. The purpose of the generator is to build a Bill Of Materials (BOM),
which is a tree structure that contains the operations involved in the production of a product.

Types of data structures
========================

The data generator is able to produce data (operations graphs) in two main tree structures:

1. n-ary trees with the levels number and children per node number given in a configuration file called "datagen.json"

                                    o
                                /  /  \
                             o   o     o
                            / \ / \   / \  \ \
                           o  o o  o  o  o  o  o
                         / \ / \ / \ / \ / \ / \
                        o   o   o   o   o   o   o

2. mixed trees which are a combination between an n-ary tree and some "vertical" trees which are attached to the children situated on the last level of the n-ary tree. 
One can see these particular trees as a "vertical" extension, which is attached to the last level of the n-ary tree. The depth of the vertical tree is configurable, as well 
as the number of children per node.

                                    o
                                /       \   \   \    \   \   \   \   \
                               o          o   o   o   o   o   o   o   o
                           /  / \        / \
                          o  o   o  o   o   o
                                 |          |
                                 o          o
                                 |          |
                                 o          o
                                            |
                                            o
                                            |
                                            o

The parameters used to generate the mixed trees can be found in the "multi-config.json" file.


Running the data generator
==========================

The code which belongs to the "multi" module is related to multiple BOMs which are executed in a batch. This approach has the advantage that a specified set of 
machines could be used to participate in the creation of multiple BOMs. The resulted BOMs could be n-ary trees or a combination between n-ary trees and vertical trees.
We named this structure "mixed trees".

Pre-requisites:
===============
Before executing the data generator in any of the two modes it is necessary to configure the parameters that will be used to produce the data. The parameters are stored 
in the "datagen/config/multi-config.json" file for the batch mode, while for the single BOM execution the config file is in "datagen/config/datagen.json".

The parameters are more or less self-explanatory and can be changed according to the user's needs.

However, there are a few sections in the configuration file which are worth mentioning:

"outputs" section:
=========

This is a list of BOMs, where the tree structure is defined.


    "max_depth" and
    "max_children"

refer to the n-ary tree and mean the depth and the maximum number of children per node.

    "vertical_tree_depth"

refers to the vertical tree structure added to the n-ary tree. The depth of the vertical tree could be also 0, case in which "min" and "max" parameters must be set to 0

The starting number of operations is taken from the "prod_number" parameter, while the number of raw materials is just a fraction of the "prod_number" (right now is hardcoded 
and set to 20%) but it will be externalized to be configurable.

After executing the program, the BOMs are saved in "datagen/multiboms" folder, in a subfolder whose name is taken from the "root_directory" parameter in the configuration file.

The data generator can be run in the following modes:

1. From the project IDE (PyCharm, Visual Studio Code, Eclipse, etc.)

In this case, to generate:
 - batch data corresponding to an n-ary tree, one can execute the "main.py" file from the "multi" package;
 - n-ary tree in a single BOM mode, one can execute "main_all.py" file from the "mono" package.

2. From the command line (terminal)

The data generator comes to a command line interface which can be used to generate data in a more flexible way. In order to run the data generator from the command line it is 
necessary to prepare the environment in which the code will run.

The following steps are required:

1. Change directory to the root of the project
2. Run the following command: 'source venv/bin/activate'
3. Run the command: 'python rungenerator.py {mono|multi} -c "configurationFilePath"
e.g.:
- python rungenerator.py mono    -c config/datagen.json
- python rungenerator.py multi   -c config/multi-config.json
- python rungenerator.py variate -c config/variants-config.json


Using generator to generate variants of an existing instance
============================================================
The generator can be used to generate instance by modifying an existing  instance generated  in "mono" style. The following variants of perturbation are supported:
- operations graph perturbation by removing or adding leaf operations. The number operations can be specified like an absolute value, or like a percentage (e.g. remove 50% of leaf operations, add number of nodes eqaul with 50% from the total number of nodes)
- operation machine alternatives modification by:
 (1) use existing machine set and add/remove alternative machines per operation. In this case additional parameters  can be set:
   (i) modified_operations_percentage - percentage of total operation that are suffering modification in machine alternatives list; default value=0.5.
   (ii) favor_machine_alternatives_increase_percentage - percentage that specifies if the appending or removing alternative machines from alternatives list is preferred; default value=0.5.
   (iii) min_alternatives/max_alternatives machines alternatives for the altered nodes, if the parameters are not specifies min_alternatives is considered to be 1 and max_alternatives is the maximum number of the alternative from the start instance.
 (2) increase / decrease existing machine set number.In this case additional parameters  can be set:
  (i) machine_no - number of machines that are added/removed from instance machine list
  (ii) min_alternatives/max_alternatives machines alternatives for all nodes, if the parameters are not specifies min_alternatives is considered to be 1 and max_alternatives is the maximum number of the alternative from the start instance.

1. From the project IDE (PyCharm, Visual Studio Code, Eclipse, etc.)

In this case, to generate variants of an existing instance, one can execute "main.py" file from the "mono_variants" package.

2. From the command line (terminal)

The following steps are required:

1. Change directory to the root of the project
2. Run the following command: 'source venv/bin/activate'
3. Run the command: 'python rungenerator.py variate -c "configurationFilePath"
e.g.: python rungenerator.py variate -c config/variants-config.json
