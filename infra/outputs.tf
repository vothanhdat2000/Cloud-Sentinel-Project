output "compliant_volume_id" {
  description = "Compliant volume ID (encrypted, tagged)."
  value       = aws_ebs_volume.compliant_vol.id
}
