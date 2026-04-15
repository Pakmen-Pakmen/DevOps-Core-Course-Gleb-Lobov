{{- define "devops-info-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "devops-info-chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "devops-info-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "devops-info-chart.labels" -}}
helm.sh/chart: {{ include "devops-info-chart.chart" . }}
{{ include "devops-info-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: api
{{- end }}

{{- define "devops-info-chart.selectorLabels" -}}
app: devops-info-service
app.kubernetes.io/name: devops-info-service
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "devops-info-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "devops-info-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "devops-info-chart.secretName" -}}
{{- if .Values.secret.name }}
{{- .Values.secret.name }}
{{- else }}
{{- printf "%s-secret" (include "devops-info-chart.fullname" .) }}
{{- end }}
{{- end }}
