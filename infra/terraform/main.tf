terraform {
  required_version = ">= 1.8"
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 6.0"
    }
  }
  # Uncomment for remote state (Oracle Object Storage):
  # backend "http" {
  #   address        = "https://objectstorage.uk-london-1.oraclecloud.com/..."
  # }
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

# ---------- VCN (Virtual Cloud Network) ----------

resource "oci_core_vcn" "finsight_vcn" {
  compartment_id = var.compartment_id
  cidr_block     = "10.0.0.0/16"
  display_name   = "finsight-vcn"
  dns_label      = "finsight"
}

resource "oci_core_internet_gateway" "igw" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.finsight_vcn.id
  display_name   = "finsight-igw"
  enabled        = true
}

resource "oci_core_route_table" "public_rt" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.finsight_vcn.id
  display_name   = "finsight-public-rt"
  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.igw.id
  }
}

resource "oci_core_subnet" "public_subnet" {
  compartment_id    = var.compartment_id
  vcn_id            = oci_core_vcn.finsight_vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "finsight-public-subnet"
  dns_label         = "public"
  route_table_id    = oci_core_route_table.public_rt.id
  security_list_ids = [oci_core_security_list.finsight_sl.id]
}

resource "oci_core_security_list" "finsight_sl" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.finsight_vcn.id
  display_name   = "finsight-security-list"

  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }

  ingress_security_rules {
    protocol = "6" # TCP
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 6443
      max = 6443
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }

  # NodePort range for k3s
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 30000
      max = 32767
    }
  }
}

# ---------- Compute Instances (ARM A1 — Always Free) ----------

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

# Ubuntu 22.04 ARM image (Oracle provided)
data "oci_core_images" "ubuntu_arm" {
  compartment_id   = var.compartment_id
  operating_system = "Canonical Ubuntu"
  shape            = "VM.Standard.A1.Flex"
  sort_by          = "TIMECREATED"
  sort_order       = "DESC"
}

resource "oci_core_instance" "k3s_server" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_id
  display_name        = "finsight-k3s-server"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_arm.images[0].id
    boot_volume_size_in_gbs = 50
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public_subnet.id
    assign_public_ip = true
    hostname_label   = "k3s-server"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/scripts/k3s-server-init.sh"))
  }

  freeform_tags = { project = "finsight", role = "k3s-server" }
}

resource "oci_core_instance" "k3s_agent" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_id
  display_name        = "finsight-k3s-agent"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ubuntu_arm.images[0].id
    boot_volume_size_in_gbs = 50
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public_subnet.id
    assign_public_ip = true
    hostname_label   = "k3s-agent"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(templatefile("${path.module}/scripts/k3s-agent-init.sh", {
      k3s_server_ip = oci_core_instance.k3s_server.public_ip
    }))
  }

  freeform_tags = { project = "finsight", role = "k3s-agent" }

  depends_on = [oci_core_instance.k3s_server]
}

# ---------- Outputs ----------

output "k3s_server_ip" {
  value       = oci_core_instance.k3s_server.public_ip
  description = "SSH to this IP to get kubeconfig: sudo cat /etc/rancher/k3s/k3s.yaml"
}

output "k3s_agent_ip" {
  value = oci_core_instance.k3s_agent.public_ip
}
