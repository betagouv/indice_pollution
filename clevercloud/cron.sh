#!/bin/bash -l

cd ${APP_HOME}

flask generate-history
flask prune-history
