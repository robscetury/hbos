# hbos
##Heterogeneous Business Object Server

HBOS is a collection of tools and ideas developed over my time as a developer.  In some many cases, solutions provided
here are the "I wish I'd done it this way," in others "I did it this way, it worked great."  Below are some example use
cases, some really basic documentation of where it is today and finally a roadmap of where this is going.

In short, there is a lot of developement that can be summarized as "Take data from this source, transform it, do some work,
and return the results to the another system." 

HBOS tries to address these situations by moving as much of this work from "code" to "configuration."  For example,
one can setup a restful API that pulls from mulitple data sources, transforms that data into a JSON object via a set of
pre-written or custom transforms.  Additionally, each call can perform "work" with the transformed data, for example
a customer placing an order can send a notification when inventory is getting low.

Example uses:
1) As a business is integrating with a vendor system, they 
may need to take data from internal data stores and transform it into a CSV, XML or JSON file to import into the vendor system.
1) A system may need to update multiple systems each using different technolgies all in one transaction.  An order system
may store the current orders in Postgres, archival orders in mongo, inventory through a separate REST api, but it's 
   advantegous to have the  client do all this with a single call into the HBOS server.
1) When piloting new enterprise software in a large organization, shared infromation can be updated thru HBOS (or someday 
HBOS will be able to subscribe to an event stream), and mulitple systems can be updated in a transactional manner -- if
   one system fails to update, the entire transaction is undone and an error returned to thru the API.
1) There are times when working on integration between two systems, where developers need to experiment, 
plan, play and model before it makes sense to commit anything to code. Since HBOS' data layer supports multiple targets,
   proof of concept code can be written using free form text files for proof of concept phase, then when the proof of concept is 
   transitioned to production ready code, the data layer can be switched to a relational, no sql database other data store.


### Configuration

The configuraiton currently consists of a single file.  Shortly, that will transition to supporting a main config file and a config.d directory of files.

The everything in the config show below is currently working, but there are some significant refactorings that remain to be done.

I'll break the file up and comment 
```json5

{
  // This section defines the ssl options for the server, 
  // the ssl and network nodes are passed to the flask constructor
  
  "ssl": {
    "ssl": false,
    "ssl_context": null
  },
  "network":{
    "port": 5055,
    "interface": "0.0.0.0"
  },
  
  // The logging node sets the options for the python logging library
  "logging": {
    "loglevel": "debug",
    "logfile": "./honeybadger.log"
  },
  // The connections node defines database connections by name, so that they can be referenced in
  // the source definitions below. Class is the full name of the closs (package/library + callable name)
  // the "args" (badly named, will change) are passed via **kwargs to the callable specified.
  //
  // At some future date, queries to named connections may be batched together and called with 
  // executemany to get a bit of a performance boost.  But that's not happening quite yet.
  "connections": {
    "sys": {
      "class": "mysql.connector.connect",
      "args": {
        "host": "10.127.127.207",
        "port": "49161",
        "user": "hbos",
        "passwd": "mypass",
        "auth_plugin": "mysql_native_password",
        "database": "sys"
      }
    },
    "db": {
      "class": "mysql.connector.connect",
      "args": {
        "host": "10.127.127.207",
        "port": "49161",
        "user": "hbos",
        "passwd": "mypass",
        "auth_plugin": "mysql_native_password"
      }
    },
    "schemas": {
      "class": "mysql.connector.connect",
      "args": {
        "host": "10.127.127.207",
        "port": "49161",
        "user": "hbos",
        "passwd": "mypass",
        "auth_plugin": "mysql_native_password",
        "database": "information_schema"
      }
    }
  },
  // The Querysets define your http endpoints (for RESTful apis, which is all that is currently supported.
  //
  // A query set is a named collection of "sources" that may hit multple data sources. The name of the queryset 
  // is the flask resource name, so you can use the same syntax when building the route.
  "querysets": [{
    // This query set pulls some data from 
    // both mysql and the file system and returns it without transforming it at all.
    "name": "/mysql/sysinfo",
    // The sources node specifies 1) the class that is responsible for pulling the data into HBOS,
    // 2) any arguments that are required by the source class (in this case the retrieve_sql [as a paramterized query]
    // and the connection name defined above.
    "sources": [
      {
        "name": "hosts",
        "class": "hbos_source.mysql_source.MySQLSource",
        "retrieve_sql" : "select * from host_summary;",
        "connection" : "sys"
      },
      {
        "name": "databases",
        "class": "hbos_source.mysql_source.MySQLSource",
        "retrieve_sql": "show databases;",
        "connection": "db"
      },
      {
        "name": "tables",
        "class": "hbos_source.mysql_source.MySQLSource",
        "retrieve_sql": "select * from SCHEMATA;",
        "connection": "schemas"
      },
      {
        "name": "filteredFiles",
        "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
        "path": "./filtered",
        "item_key": "id"
      }
    ],
    "methods": ["GET"]
  },
    {
      //The files endpoint provides full CRUD for two different sets of json files.
      // The "endPoints" node provides the OPENApi specification for the calls
    "name": "/files/",
    "endPoints": {
      "get": "./yaml/files_get.yaml"
    },
      //These sources define both a "path" (where the file exists on the file system)
      // and the property used to index items (must be unique and can be used 
      // to retrieve the item.
    "sources": [
      {
        "name": "foo",
        "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
        "path": "./foo",
        "item_key": "name"

      },
      {
        "name": "bar",
        "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
        "path": "./bar",
        "item_key": "name"
      },
      {
        "name": "filteredFiles",
        "class":  "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
        "path": "./filtered",
        "item_key": "id"
      }

    ],
    "methods": ["GET","PUT","POST","DELETE"]
  },
    {
      //As mentioned, you can use flask resource syntax to specify arguements that 
      // will be passed to the request.
      "name": "/files/<string:name>",
      "sources": [
        {
          "name": "foo",
          "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
          "path": "./foo",
          "item_key": "name"
        },
        {
          "name": "bar",
          "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
          "path": "./bar",
          "item_key": "name"
        }

      ],
      "methods": ["GET","PUT","POST","DELETE"]
    },
    {
      //This is the first end point defined with an "output" which is 
      // a transform applied to the data before it is returned to the client.
      // In this case, the items are merged so that foo(1) has a property named
      // "bar" that contains bar(1) (and foo(2) contains foo(2), etc)
      "name": "/merged_files/",
      "schemas": {

      },
      "sources": [
        {
          "name": "foo",
          "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
          "path": "./foo",
          "item_key": "name"

        },
        {
          "name": "bar",
          "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
          "path": "./bar",
          "item_key": "name"
        }

      ],
      // Multiple outputs may be specified and can be called in order.
      // Since most (all)  outputs are going to be iterating over the data 
      // it is best to keep that in mind.  If you find yourself with a huge list 
      // of outputs it may be best to write your own and do it all in one shot (inherit from outputbase)
      "outputs": [
        {
          "class": "hbos_output.merge.MergeOutput",
          "name": "MergeBarAndFoo",
          "mergeKeys": {
            "foo": [{
              "mergeSource": "bar",
              "mergeDest": "children"
            }]
          }
        }
      ],
      "methods": ["GET","PUT","POST","DELETE"]
    },
    {
      "name": "/collated_files/",
      "schemas": {

      },
      "sources": [
        {
          "name": "foo",
          "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
          "path": "./foo",
          "item_key": "name"

        },
        {
          "name": "bar",
          "class": "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
          "path": "./bar",
          "item_key": "name"
        },
        {
          "name": "filteredFiles",
          "class":  "hbos_source.jsonfilesystemstorage.JsonFileSystemStorage",
          "path": "./filtered",
          "item_key": "id"
        }

      ],
      // These output collate the files on the name property...
      // meaning that foo will have a list of attributes that where foo.name == filteredFiles.name
      // and bar will also have a list of atttributes where bar.name == filteredFiles.name
      "outputs": [
        {
          "class": "hbos_output.collate.CollateOutput",
          "name": "CollateAttributes",
          "mergeKeys": {
            "foo": [{
              "mergeSource": "filteredFiles",
              "mergeDest": "attributes",
              "mergeValue": "name",
              "mergeDestValue": "name"
            }],

                "bar": [
                  {
                    "mergeSource": "filteredFiles",
                    "mergeDest": "attributes",
                    "mergeValue": "name",
                    "mergeDestValue": "name"
                  }
                ]
              }
          },
        //This removed filtered files from the return set once we have done the collation
        {
          "class": "hbos_output.delete_source.DeleteSourceOutput",
          "name": "DelFiltered",
          "deleteKeys": ["filteredFiles"]
        },
        // LazyLoadLinks provides a way to say "There is a complex object here, but 
        // only load it when you actually need it, here is the URL.
        // This allows the client to avoid pulling down large chuncks of 
        // data that it amy not need.
        {
          "class": "hbos_output.lazy_load_links.LazyLoadLinksOutput",
          "name": "forgienKey1",
          "querysets": {
            "foo": {
              "fields": [
                {"name": "test",
                 "relName": "testId",
                  "link": "/tests/{fieldvalue}/?relName=testId"
                }
              ]
            }
          }

        },
        //This output renames the columns names,
        {
          "class": "hbos_output.column_map.ColumnMapOutput",
          "name": "columnmapper",
          "querysets": {
            "bar": {
              "fields": {
                "what": "specification",
                "flute": "valid",
                "attributes": "profile"
              }
            }
          }
        }
      ],
      "methods": ["GET","PUT","POST","DELETE"]
    }
  ]
}
```

### Roadmap

The goal is to release an intial version of HBOS in the fall of 2021, with a target of presenting at PyCon in 2022 or 2023
depending on how production ready it is and how many of the features below are supported.  Given the basic architecture of the 
system, adding additional sources, outputs and work based on users needs shouldn't be terribly difficult.

#### Protocols/Interfaces

1) RESTful API (in progress), present a restful api solely by providing a configuratio file
1) Event stream -- Connect an HBOS server to an event stream and trigger querysets/work. (Probably Kafka to start)
1) Sftp -- allow vendors to sftp files into a "share" and trigger work as a result

### Sources
1) JSON files (Done-ish) using config allow for the defintion of a CRUD api that saves JSON files to the file system
2) DB API (In progress) support for databases that support database systems that support DB API. Connection details, 
   and parameterized sql/stored procs all defined in config file.
3) MongoDB (and other no-sql databases)
4) CSV/Delimited files -- since somehow many vendors still want delimited files, provide that ability to load and "unflatten" delimited files
5) Restful APIs -- chaining in data from an external restful api
6) External process -- run a program and pull result from stdout.

### Outputs (Transforms)
1) Merge data sets into complex objects (Done)
2) Collate data sets based on key fields (Done)
3) Rename Columns (Done)
4) Data lookups (Pull, the value from one queryset based on teh value in another... I.e. Look up a group name based on group id)
5) External process -- write the current dataset to stdin, pull result from stdout

### Work (Examples)
1) Send Email
2) Update database
3) Send notification

### Other features
1) Transactions-- undo all actions and retun an error if one stage of an update, delete or create fails. (Inital code written, testing ongoing)
1) Security -- encryption/signing for configuration file to ensure it's only change by authorized parties
1) Security -- support for plugable architecture schemes (JWT to start most likely)
1) Security -- support for retreiving connection strings and passwords from secured locations (like secret server) 


