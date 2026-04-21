terraform {
  required_version = ">= 1.0"
}

provider "null" {}

# 🔹 Create Kind Cluster
resource "null_resource" "kind_cluster" {
  provisioner "local-exec" {
    command = "kind create cluster --name voting-cluster --config kind-config.yml"
  }
}

# 🔹 Load Docker Images into Kind
resource "null_resource" "load_images" {
  depends_on = [null_resource.kind_cluster]

  provisioner "local-exec" {
    command = <<EOT
      kind load docker-image candidate-service --name voting-cluster
      kind load docker-image voter-service --name voting-cluster
      kind load docker-image vote-service --name voting-cluster
      kind load docker-image result-service --name voting-cluster
      kind load docker-image gateway --name voting-cluster
    EOT
  }
}

# 🔹 Deploy Kubernetes YAMLs
resource "null_resource" "deploy_k8s" {
  depends_on = [null_resource.load_images]

  provisioner "local-exec" {
    command = "kubectl apply -f k8s/"
  }
}
