# Manual Operativo y Reglas de Negocio: Sistema de Créditos y Préstamos

## 1. Alcance y Contexto General
El Sistema de Créditos y Préstamos Automatizado (SCPA) gestiona la originación, evaluación de riesgo, aprobación y desembolso de productos crediticios de la entidad financiera. Todo requerimiento funcional que impacte este módulo debe cumplir estrictamente las directivas de la Superintendencia de Banca y Seguros y las políticas internas de gestión de riesgo crediticio.

## 2. Tipos de Productos Crediticios
1. **Crédito de Consumo Personal (CCP)**:
   - Montos: Desde $500 USD hasta $25,000 USD.
   - Plazo: De 6 a 48 meses.
   - Tasa de Interés Compensatorio Efectiva Anual (TCEA): Entre 18.5% y 42.0% según score crediticio.
2. **Crédito Vehicular (CV)**:
   - Montos: Desde $5,000 USD hasta $80,000 USD.
   - Plazo: De 12 a 60 meses.
   - Financiamiento máximo: Hasta el 80% del valor comercial de tasación del vehículo. El cliente debe aportar una cuota inicial mínima del 20%.
   - Requiere póliza de seguro vehicular endosada a favor del banco durante toda la vigencia del crédito.
3. **Crédito Hipotecario (CH)**:
   - Montos: Desde $30,000 USD hasta $500,000 USD.
   - Plazo: De 60 a 300 meses.
   - Cuota inicial mínima: 10% para primera vivienda, 20% para segunda vivienda.

## 3. Reglas de Negocio de Admisión y Validación (RN-ADM)
- **RN-ADM-001 (Edad Permitida)**: El solicitante debe tener como mínimo 21 años cumplidos al momento de la solicitud y no más de 69 años y 364 días al momento del vencimiento de la última cuota programada.
- **RN-ADM-002 (Capacidad de Endeudamiento - DTI)**: La relación cuota mensual sobre ingreso neto consolidado (Debt-to-Income / DTI) no puede superar el 35% para créditos de consumo personal ni el 40% para créditos vehiculares e hipotecarios.
- **RN-ADM-003 (Score Crediticio Central de Riesgos)**:
   - Score A (750 - 900 puntos): Aprobación automática sujeta a verificación de identidad biométrica o OTP.
   - Score B (650 - 749 puntos): Aprobación condicionada; requiere sustento adicional de ingresos (últimas 3 boletas de pago o declaración anual de impuestos).
   - Score C (500 - 649 puntos): Requiere inclusión obligatoria de un Aval / Garante Solidario con Score mínimo de 700 puntos y DTI menor al 30%.
   - Score D/E (Menor a 500 puntos o calificación deficiente/dudoso/pérdida): Rechazo automático no negociable.
- **RN-ADM-004 (Antigüedad Laboral Mínima)**:
   - Trabajadores dependientes: Mínimo 12 meses continuos de antigüedad laboral demostrable en la misma empresa o 18 meses acumulados con discontinuidad máxima de 30 días.
   - Trabajadores independientes o personas jurídicas: Mínimo 24 meses continuos con Registro Único Tributario (RUT/RUC) activo y declaraciones juradas mensuales presentadas sin omisiones.

## 4. Políticas de Garantías y Avales (RN-GAR)
- **RN-GAR-001 (Garante / Aval Solidario)**:
   - El aval asume responsabilidad mancomunada y solidaria del 100% de la deuda en caso de mora superior a 15 días calendario.
   - El aval debe firmar pagaré notarial electrónico mediante firma digital con certificado acreditado.
   - Un cliente no puede ser aval de más de 2 créditos simultáneamente dentro de la institución.
- **RN-GAR-002 (Garantía Mobiliaria)**: Para créditos vehiculares, se inscribe una garantía mobiliaria sobre el vehículo en el registro público vehicular antes de efectuar el desembolso a la concesionaria.

## 5. Proceso de Reprogramación y Refinanciamiento (RN-REP)
- **RN-REP-001**: Clientes en situación de vulnerabilidad o mora entre 16 y 60 días pueden solicitar reprogramación de saldo.
- **RN-REP-002**: La reprogramación puede extender el plazo original hasta un máximo de 12 meses adicionales, sin condonación de capital.
- **RN-REP-003**: No se permite reprogramar un crédito que ya haya sido reprogramado en los últimos 12 meses previos.
- **RN-REP-004**: Toda reprogramación modifica la tasa de interés base en un recargo de riesgo de +1.5% TCEA y recalcula el cronograma bajo el sistema de amortización francés.

## 6. Canales y Desembolso (RN-DES)
- **RN-DES-001**: El desembolso para créditos de consumo personal se realiza exclusivamente a una cuenta de ahorros o corriente a nombre del titular en la misma entidad.
- **RN-DES-002**: Para créditos vehiculares, el desembolso nunca se abona al cliente; se emite cheque de gerencia o transferencia directa a la cuenta corporativa validada del concesionario autorizado.
- **RN-DES-003**: Todo desembolso superior a $10,000 USD requiere validación biométrica facial o confirmación presencial con token de seguridad FIDO2/clave dinámica.
