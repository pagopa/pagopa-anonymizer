# sh run_performance_test.sh <local|dev|uat|prod> <load|stress|spike|soak|...> <script-name> <db-name> <subkey>

ENVIRONMENT=$1
TYPE=$2
SCRIPT=$3
DB_NAME=$4
SUBSCRIPTION_KEY=$5

if [ -z "$ENVIRONMENT" ]
then
  echo "No env specified: sh run_performance_test.sh <local|dev|uat|prod> <load|stress|spike|soak|...> <script-name> <db-name> <subkey>"
  exit 1
fi

if [ -z "$TYPE" ]
then
  echo "No test type specified: sh run_performance_test.sh <local|dev|uat|prod> <load|stress|spike|soak|...> <script-name> <db-name> <subkey>"
  exit 1
fi
if [ -z "$SCRIPT" ]
then
  echo "No script name specified: sh run_performance_test.sh <local|dev|uat|prod> <load|stress|spike|soak|...> <script-name> <db-name> <subkey>"
  exit 1
fi

export env=${ENVIRONMENT}
export type=${TYPE}
export script=${SCRIPT}
export db_name=${DB_NAME}
export sub_key=${SUBSCRIPTION_KEY}

stack_name=$(cd .. && basename "$PWD")
docker compose -p "${stack_name}-k6" up -d --remove-orphans --force-recreate --build
docker logs -f k6
docker stop nginx
