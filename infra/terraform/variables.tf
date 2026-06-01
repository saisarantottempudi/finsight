variable "tenancy_ocid" {
  description = "Oracle Cloud tenancy OCID"
  type        = string
}

variable "user_ocid" {
  description = "Oracle Cloud user OCID"
  type        = string
}

variable "fingerprint" {
  description = "API key fingerprint"
  type        = string
}

variable "private_key_path" {
  description = "Path to OCI API private key"
  type        = string
  default     = "~/.oci/oci_api_key.pem"
}

variable "region" {
  description = "Oracle Cloud region"
  type        = string
  default     = "uk-london-1"
}

variable "compartment_id" {
  description = "Compartment OCID"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for VM access"
  type        = string
}
