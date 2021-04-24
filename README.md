# hbos
Heterogeneous Business Object Server

HBOS is a simple business data object server.  It allows for a simple restful API that hits multiple data sources, formats the output and returns the data in a selected format.

Example Usages:
  1. Quick prototyping of a dummy api writting to/from a database
  1. In an enterprise, pulling and collating data in from multiple data sources.  For example, User data maybe stored in LDAP, vacation policies in an Oracle based HR database, order fulfilment tracked via a mongo database and throughput tracked via a RESTFul api.
  1. Getting legacy systems to interact with modern systems.  In a company that is partially transitioned from a legacy system, customers updated via HBOS can update both the legacy and new systems, even remapping the new systems schema to the old system.

e
