provider "local" {}

resource "local_file" "recovery_log" {
  content  = "Infrastructure recovery initiated at ${timestamp()}"
  filename = "healed_node.txt"
}
