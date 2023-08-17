# {{cookiecutter.project_name}}

The purpose of this project is to provide a fully functional implementation of simple applications that is fully
integrated with the console.redhat.com platform, to serve as an example for new teams onboarding into the platform
to create their own applications.

## Prerequisites

- This project requires Python 3 and Django REST Framework to run. We recommend to use at least Python 3.10, but any
version 3.6+ will work too. Once you have those all you will want to create and activate a virtual environment for
the app and install Django. The project uses a Makefile to simplify getting started.

- This project uses [Makefile](https://www.gnu.org/software/make/). There are several recipes included to ease
the task of installing and running the application.

**NOTE**: Most of the Makefile recipes enforce the use of
[virtual environments](https://docs.python.org/3/library/venv.html), and by default they will check if there is a
virtual environemnt activated, refusing to run otherwise.

### **Optional for deploying to ephemeral environments:**

- You need to be onboarded to the Ephemeral cluster to be able to deploy to it. If you're not, please make sure to
check the documentation
[here](https://consoledot.pages.redhat.com/docs/dev/creating-a-new-app/using-ee/getting-started-with-ees.html)

- [Bonfire](https://pypi.org/project/crc-bonfire) is required to run the deployment to Ephemeral environment recipes.
- A public* Quay.io repository is required to host your container images and deploy them to an Ephemeral environment.

* We encourage you to create a public Quay.io repository to host the images. While a private repository will also work,
you'll have to provide a Secret to the ephemeral namespace SA to be able to pull the image.

## Installing the application

Most of the recipes require a Python virtual environment to be active. This is to avoid installing dependencies to your
local user's namespace.

To create and activate a virtual environment you can use the `create_venv` recipe:

```shell
make venv_create && source .venv/bin/activate
```

To install the project, run

```shell
make install
```

To install all the optional development dependencies (including **Bonfire**) run instead

```shell
make install_dev
```

The next sections will assume you have a virtual environment active

## Running the tests

Tests can be run using the `test` recipe:

```
make test
```

This would run the tests using the default configured test runner using Django `test` command from `manage.py` script.

### Generating code coverage

In case you want to generate an HTML report of your code coverage, you can do so by using the `coverage` recipe

```
make coverage
```

This will:

- Install the development depenencies (to install [coverage.py])
- Run the tests
- Generate a report (by default, the report format will be HTML).

you can override the report format to either XML, JSON or HTML format using the `COVERAGE_REPORT_FORMAT` variable:

```
make COVERAGE_REPORT_FORMAT=json coverage
```

To check the available supported coverage formats, please check
[Coverage.py docs](https://coverage.readthedocs.io/en/7.2.7/#capabilities)


## Running the application

There are Makefile recipes to run the application directly or in a container

### Running as a local process

To run this project locally simply:

```shell
make run
```

After running that command you should see this output:

```shell
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
June 14, 2023 - 12:34:18
Django version 4.2.2, using settings 'backend_starter_app.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Navigate to http://127.0.0.1:8080 to access to the Django application's web console.

### Running in a container locally:

To run this project on a container using your local container engine of choice we provide Makefile recipes for both
[podman](podman.io) and [Docker](docker.com)

#### Build the container image

To build the contaienr image, simply one of these commands, depending if you're using podman or docker:

```shell
# build with podman
make build-image

# build with docker
make build-image-docker
```

#### Run the container image

To run the recently built image, similarly to how you built the image in the previous section, use one of these commands

```shell
# run with podman
make run-container

# run with docker
make run-container-docker
```

## Deploying to an Ephemeral namespace

In order to deploy to an Ephemeral cluster, you need to build and push your container image to a Quay.io repository, and
you need to login against the Ephemeral cluster. (please, check the [Pre-requisites section to know how to onboard to
the Ephemeral cluster in case you are not onboarded yet).

Finally, you'll need to reserve a namespace in advance in the Ephemeral cluster.

### Reserve a namespace in the Ephemeral cluster

If you don't already have bonfire installed, you can use `make install-dev` to install it to your virtual environment.
Reserve a target namespace in the Ephemeral namespace and save it for later:

```
make bonfire_reserve_namespace
bonfire namespace reserve
2023-07-02 21:08:56 [    INFO] [          MainThread] Checking for existing reservations for 'Victoremepunto'
2023-07-02 21:08:56 [    INFO] [          MainThread] checking for available namespaces to reserve...
2023-07-02 21:08:57 [    INFO] [          MainThread] pool size limit is defined as 0 in 'default' pool
2023-07-02 21:08:57 [    INFO] [          MainThread] processing namespace reservation
2023-07-02 21:08:57 [    INFO] [          MainThread] running (pid 1771071): oc apply -f -
2023-07-02 21:08:58 [    INFO] [         pid-1771071]  |stdout| namespacereservation.cloud.redhat.com/bonfire-reservation-12538be0 created
2023-07-02 21:08:58 [    INFO] [          MainThread] waiting for reservation 'bonfire-reservation-12538be0' to get picked up by operator
2023-07-02 21:08:58 [    INFO] [          MainThread] namespace 'ephemeral-cv17hi' is reserved by 'Victoremepunto' for '1h' from the default pool
2023-07-02 21:08:58 [    INFO] [          MainThread] running (pid 1771118): oc project ephemeral-cv17hi
2023-07-02 21:08:59 [    INFO] [         pid-1771118]  |stdout| Now using project "ephemeral-cv17hi" on server "https://api.c-rh-c-eph.8p0c.p1.openshiftapps.com:6443".
2023-07-02 21:08:59 [    INFO] [          MainThread] namespace console url: https://console-openshift-console.apps.c-rh-c-eph.8p0c.p1.openshiftapps.com/k8s/cluster/projects/ephemeral-cv17hi
ephemeral-cv17hi
```

Save the ephemeral namespace name for later, you can export it to an environment variable named `NAMESPACE` for
simplicity.

### Building and pushing the backend starter application image

Make sure to log in to your Quay.io account before this step, this guide will asume you have created a repository in
Quay to host your images. We **encourage you to use a public repository** to simplify the process, since a private
repository will require you to create an additional secret on the Ephemeral namespace to be able to deploy the image.

Make sure you're logged in against Quay using the `login` command of either `podman` or `docker` with write
permissions against the target image repository.

```shell
# podman
podman login quay.io

# docker
podman login quay.io
```

We should be ready to build and push a container image. The included Makefile has recipes to create and push an image to
the user's personal organization in Quay.io

To build and push the application's image simply run:

```shell
# with podman
make build-image push-image

# with docker
make build-image-docker push-image-docker
```

Once pushed, the image needs to be pulled by the Clowder operator. If the repository is `public` there should be no
further requirements, and you can simply skip the next section straight into "Deploy your application".

### PRIVATE REPOSITORIES ONLY: Creating and adding a pull secret to the namespace for private registries in Quay.io.

Once the image is pushed to the user's org In Quay, you should create a pull secret and add it to the ClowderEnvironment's
list of `PullSecrets`

To generate the secret:

- Head to Quay.io, log into your account, and click on your user's org.
- Click on the left side on "Robot accounts" and create a new robot account
- Provide a name for your robot account.
- Select the `backend-starter-app-python` repository, you should only require `read` permissions.
- Click on the recently created robot account, and select "Kubernetes secret".
- Click on the link to download the secret in YAML format under "Step 1: Download secret" section.

This secret must be added to the list of `PullSecrets` of the `ClowdEnvironment` of the target namespace in order
to be able to pull the application image from the private registry

You need to create this secret in the target namespace and configure it in the ClowdEnvironment. To do so:

- Create the secret in the target namespace using the YAML file you downloaded from Quay.io

```
oc create -f /path/to/your/secret.yaml -n "$NAMESPACE"
secret/vmugicag-somesecretname-pull-secret created
```

Your secret's name is required, you can check it inside the YAML that contains the definition. It's probably in the format
"your user id"-"secret name"-pull-secret

You will require this name later to refer to the secret on the ClowdEnvironment

- Edit the ClowdEnvironment and add the PullSecret to the list:

```
oc get ClowdEnvironment -o name | grep "$NAMESPACE" | xargs oc edit
```

This should open your system's default editor with the YAML definition of the ClowdEnvironment.
You should locate and add the secret to the PullSecrets list:

```YAML
     pullSecrets:
     # other secrets may be listed here ...
     - name: backend-starter-app-python    # <-- Add your secret's name
       namespace: your-target-namespace    # <-- Add the ephemeral namespace name here
```

### Deploy your application to the Ephemeral namespace

use the `bonfire_deploy` recipe to deploy your application into an ephemeral namespace.
use the NAMESPACE variable to pass the name of the target namespace

```
# make NAMESPACE=your-ephemeral-namespace bonfire_deploy
```

The application should deploy to your reserved ephemeral namespace within a few minutes.

## Additional Makefile recipes

### Installing rh-pre-commit

We've added a recipe to install the
[rh-pre-commit](https://gitlab.corp.redhat.com/infosec-public/developer-workbench/tools/-/tree/main/rh-pre-commit) to this
repository. This will prevent you from accidentally committing credentials, tokens, or other secrets to your repo. To install
the pre-commit run:

```bash
$ make install_pre_commit
```

Follow the prompt to receive a token and complete the install.

Once complete you can test the precommit by running in the repo:

```bash
# Note: before testing remove the gitleaks:allow comment.
# It is there to prevent false positives when committing changes to the README
echo 'secret="EdnBsJW59yS6bGxhXa5+KkgCr1HKFv5g"' > secret # gitleaks:allow
git add secret
git commit
```

### Installing the rest of the pre-commits

We are using the python package [pre-commit](https://pre-commit.com/) to handle the setup and maintenance pre-commit hooks. We
have pre-configured a few commit hooks but we encourage modifying the `.pre-commit-config.yaml` to fit your project as needed.
If you don't already have a virtual environment setup, you can use the following commands to do that.

```bash
# Create the virtual environment
$ make venv_create
# Activate the virtual environment
$ source .venv/bin/activate
```

Once you have sourced your virtual environment you can install the pre-commit package and the hooks themselves with the following
commands:

```bash
# Install pre-commit hooks by installing the project's dependencies and development dependencies
$ make install_dev
```
**Note**: none of the hooks we provide are required but are just our recommendations.

### Configuring Prometheus Metrics

The Prometheus client is handled by [django-prometheus](https://github.com/korfuri/django-prometheus). This provides the
prometheus_client globally so adding metrics is as simple as making new objects to track what you want. Documentation on
how to add these metrics can be found [here](https://github.com/prometheus/client_python#instrumenting).

### Configuring Logging

For logging configuration, we are using the Django's native configuration tools with
[python-json-logger](https://github.com/madzak/python-json-logger) to put the logs in JSON format. More information on how to
further configure logging can be found [here](https://docs.djangoproject.com/en/4.2/topics/logging/#configuring-logging).
