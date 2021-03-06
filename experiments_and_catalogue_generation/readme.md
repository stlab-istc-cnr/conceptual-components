# Experiments and catalogue generation

This Java project allows you to:
- Run the experiments
- Generate the Catalogue of Conceptual Components and Observed Ontology Design Patterns.

The project can be built and executed by using maven.

To build the project open the terminal, move to the root folder of the project and run the following command:

    mvn install

To run the experiments type

    mvn exec:java  -Dexec.cleanupDaemonThreads=false -Dexec.mainClass="odpd.AnalyseAlignments"  -Dexec.args="/path/to/Experiments_materials/"

To generate the Catalogue type

    mvn exec:java  -Dexec.cleanupDaemonThreads=false -Dexec.mainClass="odpd.GenerateCatalogue"  -Dexec.args="/path/to/Experiments_materials/ /path/to/OutFolder/ CORPUS_NAME NUMBER_OF_ONTOLOGIES_WITHIN_THE_CORPUS CLUSTERING_CSV_FILE_WITHIN_EXPERIMENTS_MATERIALS FOLDER_NAME_WITHIN_EXPERIMENTS_MATERIALS_CONTAINING_GENERATED_COMMUNITIES FOLDER_NAME_WITHIN_EXPERIMENTS_MATERIALS_CONTAINING_SOURCE_ONTOLOGIES"

This command generates the Catalogue website, therefore you can go to OutFolder and open the index.html file to access the generated Catalogue.
