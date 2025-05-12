CREATE DATABASE IF NOT EXISTS universidad;
-- Use the universidad database
USE universidad;

-- Grant privileges
GRANT ALL PRIVILEGES ON universidad.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- 3) Crear el usuario de aplicación y otorgarle los mismos permisos
CREATE USER IF NOT EXISTS 'app_user'@'%' 
  IDENTIFIED BY 'AzaKs1mWzDpG8eo';
-- Concede solo lo imprescindible
GRANT SELECT, INSERT, UPDATE 
  ON universidad.* 
  TO 'app_user'@'%';
FLUSH PRIVILEGES;

CREATE USER IF NOT EXISTS 'Movilidad'@'%' 
  IDENTIFIED BY '3KOO7iO2Bu2yhH4';

GRANT SELECT
  ON universidad.*
  TO 'Movilidad'@'%';

FLUSH PRIVILEGES;
