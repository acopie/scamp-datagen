PLEASE DO NOT DELETE THIS FILE!!
===============================

Types of data structures
========================

The data generator is able to produce data in two main tree structures:
1. n-ary trees with the level number and children per node number given in a configuration file called "datagen.json"

                                    o
                                /  /  \
                             o   o     o
                            / \ / \   / \  \ \
                           o  o o  o  o  o  o  o
                         / \ / \ / \ / \ / \ / \
                        o   o   o   o   o   o   o

2. mixed trees which are a combination between an n-ary tree and some "vertical" trees which are attached to the
   children situated on the last level of the n-ary tree.

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

The parameters used to generate the mixed trees can be found in the "mixed-trees.json" file.

Running the data generator
==========================

Pre-requisites: before executing the data generator in any of the two modes it is necessary to configure the parameters
that will be used to produce the data. The parameters are stored in the "datagen.json" file for the n-ary trees and in
the "mixed-trees.json" file for the mixed trees. The parameters are more or less self-explanatory and can be changed
according to the user's needs.

The data generator can be run in two modes:

1. From the project IDE (PyCharm, Eclipse, etc.)

In this case, to generate data corresponding to a n-ary tree, one can execute the main_all.py file

2. From the command line (terminal)

The data generator comes to a command line interface which can be used to generate data in a more flexible way. In order
to run the data generator from teh command line it is necessary to prepare the environment in which the code will run.
The following steps are required:

1. Change directory to the root of the project
2. Run the following command: 'source venv/bin/activate'
3. After the virtual environment is activated, run the command: 'python datagen/datagen.py --type n-ary' or
    'python datagen/datagen.py --type mixed' to produce an n-ary structure, respectively a mixed structure.
