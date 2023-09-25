def secrets = [
    [path: params.VAULT_PATH_SVC_ACCOUNT_EPHEMERAL, engineVersion: 1, secretValues: [
        [envVar: 'OC_LOGIN_TOKEN', vaultKey: 'oc-login-token'],
        [envVar: 'OC_LOGIN_SERVER', vaultKey: 'oc-login-server']]],
    [path: params.VAULT_PATH_QUAY_PUSH, engineVersion: 1, secretValues: [
        [envVar: 'QUAY_USER', vaultKey: 'user'],
        [envVar: 'QUAY_TOKEN', vaultKey: 'token']]],
    [path: params.VAULT_PATH_RHR_PULL, engineVersion: 1, secretValues: [
        [envVar: 'RH_REGISTRY_USER', vaultKey: 'user'],
        [envVar: 'RH_REGISTRY_TOKEN', vaultKey: 'token']]]
]

def configuration = [vaultUrl: params.VAULT_ADDRESS, vaultCredentialId: params.VAULT_CREDS_ID, engineVersion: 1]

pipeline {
    agent { label 'rhel8' }
    options {
        timestamps()
    }
    environment {
        PROJECT_NAME='backend-starter-app-python'
        QUAY_ORG='cloudservices'
    }
    stages {
        stage('Build the PR project template and setup') {
            steps {
                withVault([configuration: configuration, vaultSecrets: secrets]) {
                    sh '''
                        make venv_create
                        source .venv/bin/activate
                        make setup
                        rm -rf .venv

                        oc login --token=${OC_LOGIN_TOKEN} --server=${OC_LOGIN_SERVER}
                    '''
                    dir("${PROJECT_NAME}") {
                        sh '''
                            make venv_create
                            source .venv/bin/activate
                            make install_dev
                        '''
                    }
                }
            }
        }
        stage('Build temporary image') {
            steps {
                dir("${PROJECT_NAME}") {
                    withVault([configuration: configuration, vaultSecrets: secrets]) {
                        sh '''
                            source .venv/bin/activate
                            make build-image
                            make quay_login
                            make push-image
                        '''
                    }
                }
            }
        }
        stage('Deploy on Ephemeral') {
            steps {
                dir("${PROJECT_NAME}") {
                    script {
                        NAMESPACE = sh(returnStdout:true, script: '''
                            source .venv/bin/activate
                            make bonfire_reserve_namespace
                        ''').trim()
                    }
                    echo "Namespace reserved:${NAMESPACE}"
                    sh """
                        source .venv/bin/activate
                        NAMESPACE=${NAMESPACE} make bonfire_deploy
                        """
                }
            }
        }
    }
    post {
        always {
            script {
                if (NAMESPACE) {
                    dir("${PROJECT_NAME}") {
                        echo "Releasing namespace: ${NAMESPACE}"
                        sh """
                            source .venv/bin/activate
                            NAMESPACE=${NAMESPACE} make bonfire_release_namespace
                        """
                    }
                }
            }
        }
    }
}
