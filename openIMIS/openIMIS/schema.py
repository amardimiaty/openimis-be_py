import graphene
from .openimisapps import openimis_apps
from graphene_django.debug import DjangoDebug

all_apps = openimis_apps()
queries = []
mutations = []
for app in all_apps:
    try:
        # If we only __import__ the module, the schema is not loaded and .schema will fail. Adding an import to force
        # Python to load it would work but not from __init__.py because Django models are not loaded yet at that point.
        # Importing claim.schema still returns the claim module but it forces the loading of schema.
        # This code is executed on first access to the Graphene API
        query = __import__(f"{app}.schema").schema.Query
        if query:
            queries.append(query)

        if __import__(f"{app}.schema").schema.Mutation:
            mutation = __import__(f"{app}.schema").schema.Mutation
            if mutation:
                mutations.append(mutation)

    except ModuleNotFoundError:
        pass  # The module doesn't have a schema.py, just skip
    except AttributeError:
        pass  # The module doesn't have a Query or Mutation, just ignore


class Query(*queries, graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(*mutations, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
