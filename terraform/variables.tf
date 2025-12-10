variable "location" {
  description = "Azure region"
  default     = "East US"
}

variable "docker_username" {
  description = "Docker Hub Username"
  type        = string
  default     = "vedangj044"
}

variable "docker_password" {
  description = "Docker Hub Password/Token"
  type        = string
  sensitive   = true
  default     = "ky3/8Xn?R%vF2M#"
}
