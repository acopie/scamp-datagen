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

The code which belongs to the "multi" module is related to multiple BOMs which are executed in a batch. The resulted
BOMs could be n-ary trees or a combination between n-ary trees and vertical trees. We named this structure "mixed trees".

Pre-requisites: before executing the data generator in any of the two modes it is necessary to configure the parameters
that will be used to produce the data. The parameters are stored in the "datagen/config/multi-config.json" file for the
batch mode, while for the single BOM execution the config file is in datagen/config/datagen.json.

The parameters are more or less self-explanatory and can be changed according to the user's needs.

However, there are a few sections in the configuration file which are worth mentioning:

"outputs" section: is a list of BOMs, where te tree structure is defined.
    "max_depth" and
    "max_children"
refer to the n-ary tree and mean the depth and the maximum number of children per node.
    "vertical_tree_depth"
refers to the vertical tree structure added to the n-ary tree. The depth of the vertical tree could be also 0, case in
which "min" and "max" parameters must be set to 0

The starting number of operations is taken from the "prod_number" parameter, while the number of raw materials is just a
fraction of the "prod_number" (right now is hardcoded and set to 20%) but it will be externalized to be configurable.

After executing the program, the BOMs are saved in datagen/multiboms folder, in a subfolder who's name is taken from the
"root_directory" parameter in the configuration file.

The data generator can be run in two modes:

1. From the project IDE (PyCharm, Eclipse, etc.)

In this case, to generate batch data corresponding to a n-ary tree, one can execute the main.py file from the "multi"
package, while for executing a n-ary tree in a single BOM mode, one main execute main_all.py file from the "mono" package.

2. From the command line (terminal)

The data generator comes to a command line interface which can be used to generate data in a more flexible way. In order
to run the data generator from teh command line it is necessary to prepare the environment in which the code will run.
The following steps are required:

1. Change directory to the root of the project
2. Run the following command: 'source venv/bin/activate'
3. Run the command: 'python rungenerator.py {mono|multi}


