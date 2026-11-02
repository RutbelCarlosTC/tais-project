# Políticas de Seguridad, Autenticación y Prevención del Fraude

## 1. Gestión de Sesión y Canales Digitales (SEC-SES)
- **SEC-SES-001 (Tiempo de Inactividad)**: Las sesiones activas en la banca por internet o banca móvil expiran automáticamente tras 5 minutos de inactividad sin interacción del usuario.
- **SEC-SES-002 (Concurrencia de Dispositivos)**: No se permite el inicio de sesión concurrente desde múltiples dispositivos con las mismas credenciales. Un nuevo inicio de sesión cierra forzosamente la sesión previa y registra una alerta preventiva.
- **SEC-SES-003 (Dispositivo de Confianza)**: El enrolamiento de un nuevo smartphone como dispositivo seguro requiere validación biométrica facial activa contra la base de datos nacional de identificación o verificación presencial en agencia.

## 2. Autenticación de Dos Factores y Desafíos de Seguridad (SEC-MFA)
- **SEC-MFA-001**: Toda operación monetaria de transferencia, pago de servicios superior a $100 USD o modificación de datos sensibles (teléfono, correo, clave) exige autenticación reforzada de dos factores (2FA).
- **SEC-MFA-002 (Mecanismos Autorizados)**:
   1. Token digital criptográfico generado por la aplicación móvil (TOTP basado en RFC 6238 con ventana de 30 segundos).
   2. Clave dinámica enviada por SMS/WhatsApp únicamente para operaciones de bajo riesgo (< $150 USD).
   3. Firma biométrica facial 3D (liveness detection activo).
- **SEC-MFA-003**: Si el usuario falla 3 intentos consecutivos de ingreso del factor de autenticación, el canal digital queda bloqueado preventivamente durante 24 horas o hasta desbloqueo asistido con operador de seguridad.

## 3. Límites Transaccionales y Transferencias Interbancarias (SEC-LIM)
- **SEC-LIM-001 (Límite Diario Estándar)**: El límite máximo acumulado por día para transferencias a terceros e interbancarias inmediatas es de $3,000 USD o su equivalente en moneda local para clientes estándar.
- **SEC-LIM-002 (Ampliación Temporal de Límites)**:
   - El cliente puede solicitar ampliación temporal del límite hasta por $15,000 USD por un lapso no mayor a 24 horas.
   - Requiere validación de doble factor (Token Digital + Reconocimiento Facial) y confirmación de origen de fondos.
   - Tiene un periodo de enfriamiento (cooling-off period) de 2 horas antes de que la ampliación sea efectiva, como protección ante fraudes por secuestro exprés o ingeniería social.
- **SEC-LIM-003 (Transferencias Interbancarias Inmediatas)**: Operan las 24 horas los 7 días de la semana mediante la Cámara de Compensación Electrónica. Montos individuales mayores a $10,000 USD se canalizan obligatoriamente por liquidación diferida en horario bancario hábil (09:00 a 16:30 hrs).

## 4. Detección de Fraude y Bloqueo de Tarjetas (SEC-FRD)
- **SEC-FRD-001 (Reglas de Disparo de Alerta de Fraude)**:
   - Disparo por velocidad geográfica imposible (ej. compras presenciales con diferencia menor a 60 minutos en ciudades distintas).
   - Patrón de consumo anómalo (monto superior en 300% a la media histórica del cliente en comercios de alto riesgo).
   - Más de 3 intentos fallidos de PIN en cajero automático o CVV incorrecto en e-commerce en menos de 10 minutos.
- **SEC-FRD-002 (Protocolo de Bloqueo Automático)**:
   - Bloqueo preventivo de la tarjeta de crédito o débito afectada de manera inmediata.
   - Envío simultáneo de notificación push, SMS y correo electrónico al cliente indicando el motivo y los últimos 4 dígitos de la tarjeta.
- **SEC-FRD-003 (Protocolo de Desbloqueo Seguro)**:
   - El cliente solo puede desbloquear la tarjeta a través del canal de atención telefónica especializada antifraude o en ventanilla bancaria con DNI/documento físico y huella dactilar biométrica.
   - Si la tarjeta fue bloqueada por confirmación de fraude efectivo, no procede el desbloqueo; se debe emitir un nuevo plástico y generar una nueva numeración virtual en un plazo máximo de 48 horas hábiles.
