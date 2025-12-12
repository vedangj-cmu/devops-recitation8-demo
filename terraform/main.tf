terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.13"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "aks_rg" {
  name     = "monitoring-demo-aks-rg"
  location = "East US"
}

resource "azurerm_log_analytics_workspace" "aks_workspace" {
  name                = "monitoring-demo-aks-workspace"
  location            = azurerm_resource_group.aks_rg.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_application_insights" "aks_appinsights" {
  name                = "monitoring-demo-aks-ai"
  location            = azurerm_resource_group.aks_rg.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  workspace_id        = azurerm_log_analytics_workspace.aks_workspace.id
  application_type    = "web"
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "monitoring-demo-aks"
  location            = azurerm_resource_group.aks_rg.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  dns_prefix          = "monitoring-demo-aks"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = "demo"
  }
}

provider "kubernetes" {
  host                   = azurerm_kubernetes_cluster.aks.kube_config.0.host
  client_certificate     = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_certificate)
  client_key             = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.client_key)
  cluster_ca_certificate = base64decode(azurerm_kubernetes_cluster.aks.kube_config.0.cluster_ca_certificate)
}

resource "kubernetes_deployment" "app" {
  metadata {
    name = "monitoring-demo-app"
    labels = {
      app = "monitoring-demo"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "monitoring-demo"
      }
    }

    template {
      metadata {
        labels = {
          app = "monitoring-demo"
        }
      }

      spec {
        container {
          image = "vedangj044/monitoring-demo:latest"
          name  = "monitoring-demo-app"

          port {
            container_port = 8000
          }

          env {
            name  = "APPLICATIONINSIGHTS_CONNECTION_STRING"
            value = azurerm_application_insights.aks_appinsights.connection_string
          }

          env {
            name  = "OTEL_SERVICE_NAME"
            value = "monitoring-demo-aks"
          }

          image_pull_policy = "Always"
        }
      }
    }
  }
}

resource "kubernetes_service" "app_service" {
  metadata {
    name = "monitoring-demo-service"
  }
  spec {
      selector = {
        app = kubernetes_deployment.app.metadata.0.labels.app
      }
      port {
        port        = 80
        target_port = 8000
      }

      type = "LoadBalancer"
  }
}

output "aks_app_url" {
  value = "http://${kubernetes_service.app_service.status.0.load_balancer.0.ingress.0.ip}"
}
