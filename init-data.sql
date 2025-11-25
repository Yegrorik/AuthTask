INSERT INTO users (name, surname, email, hashed_password, role, is_active) VALUES
(
    'Admin', 
    'User', 
    'admin@example.com', 
    '$argon2id$v=19$m=65536,t=3,p=4$g5RGiB07S9AzDx+l7GyxeQ$8GvSgmPDAZXNOPL/d0WOKkYngYivHv2AquUcarv2Bto', -- admin123
    'admin', 
    true
),
(
    'Manager', 
    'User', 
    'manager@example.com', 
    '$argon2id$v=19$m=65536,t=3,p=4$yo/gkifu14Su83gzdgEgXw$05LWMVT27+PTQ7cVGpNLALs3vOPyxDypdMB+4ObZNUk', -- manager123
    'manager', 
    true
),
(
    'Regular', 
    'User', 
    'user@example.com', 
    '$argon2id$v=19$m=65536,t=3,p=4$IM0loXJqUR/HMnjte2M5Fw$4rYYFFlxNnsF/zeovVSMZHDRAtuAwg1ZeF8PKbKxWs8', -- user123
    'user', 
    true
)
ON CONFLICT (email) DO NOTHING;