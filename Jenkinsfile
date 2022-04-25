node('jenkins-slave') {
  
       stage('Checkout Source') {
      
        git url:'https://github.com/AkilAkil/exporter.git', branch:'master'
      
    }
    
    stage("Build image") {
      sh(script: """
           set +x
           echo "*************************************"
           echo "****  Building Docker Image    ******"
           echo "*************************************"
       """)
            myapp = docker.build("flexran.exporter","./")
            
        }
    stage('Publish') {
        sh(script: """
           set +x
           echo "***************************************"
           echo "***Publish Docker image to Registry****"
           echo "***************************************"

        docker  tag flexran.exporter:latest ${dockerhub}
        docker push ${dockerhub}
        """)
    }
    

    stage('Apply Kubernetes files') {
      sh(script: """
           set +x
           echo "*************************************"
           echo "****Deploy in Kubernetes cluster*****"
           echo "*************************************"
       """)

        withCredentials([file(credentialsId: 'mykubeconfigfile', variable: 'KUBECONFIG')]){
        sh 'kubectl apply -f exporter.yaml'
    }
  }
}
