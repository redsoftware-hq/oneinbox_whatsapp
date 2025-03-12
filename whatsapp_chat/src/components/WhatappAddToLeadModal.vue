<template>
  <Dialog v-model="show" :options="{ title: `Add ${form_name}`, size: '2xl' }">
    <template #body-content>
      <div
        v-for="(field, index) in dynamicFields"
        :key="index"
        class="p-2"
        :class="{ 'overflow-y-auto max-h-96': dynamicFields.length > 8 }"
      >
        <FormControl
          v-model="lead[field.lead_field_name]"
          :type="mapInputType(field.doctype_field_type)"
          :size="'sm'"
          :variant="'subtle'"
          :placeholder="field.lead_field_name"
          :label="formatLabel(field.lead_field_name)"
          :options="getOptions(field)"
          :as="mapInputType(field.doctype_field_type) === 'autocomplete' ? 'autocomplete' : null"
        />
      </div>
      <div class="mt-4 flex justify-end text-black">
        <button class="mr-2 px-4 py-2 bg-gray-300 rounded" type="button" @click="closeDialog">Cancel</button>
        <button class="px-4 py-2 bg-gray-700 text-white rounded" type="button" @click="submitLead">Save Lead</button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watchEffect, defineProps } from "vue";
import { FormControl, createResource } from "frappe-ui";
import { toRaw } from "vue";
import { emitter } from "../utils/eventBus";

const props = defineProps({
  contact_number: String,
  first_name: String,
  showAddLeadModal: Boolean,
});

const show = ref(props.showAddLeadModal);
const csrfToken = ref(window.frappe.csrf_token || "");

const fieldMappingsResource = createResource({
  url: "/api/method/frappe_whatsapp.api.whatsapp.get_leadmapping_fields",
  auto: true,
  headers: { "X-Frappe-CSRF-Token": csrfToken.value },
});

const formDataResource = createResource({
  url: "/api/method/frappe_whatsapp.api.whatsapp.get_form_data",
  auto: true,
  headers: { "X-Frappe-CSRF-Token": csrfToken.value },
});

const dynamicFields = ref([]);
const lead = ref({});
const form_name = ref("");

watchEffect(() => {
  show.value = props.showAddLeadModal;
});

const closeDialog = () => {
  show.value = false;
};

watchEffect(() => {
  if (fieldMappingsResource.data?.field_mappings) {
    dynamicFields.value = fieldMappingsResource.data.field_mappings;
    form_name.value = fieldMappingsResource.data.mappings.lead_reference_doctype;

    lead.value = dynamicFields.value.reduce((acc, field) => {
      if (field.doctype_field_type === "Select" || field.doctype_field_type === "Link") {
        acc[field.lead_field_name] = field.select_options?.[0] || field.linked_records?.[0] || "";
      } else {
        acc[field.lead_field_name] = "";
      }
      return acc;
    }, {});

    lead.value.contact_number = props.contact_number || "";
    lead.value.first_name = props.first_name || "";
    lead.value.created_on = new Date().toISOString().split('T')[0];
  }
});

const mapInputType = (doctypeFieldType) => {
  const typeMap = {
    Data: "text",
    Phone: "tel",
    Date: "text",
    Select: "autocomplete",
    Link: "autocomplete",
  };
  return typeMap[doctypeFieldType] || "text";
};

const formatLabel = (key) => key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());

const getOptions = (field) => {
  if (field.doctype_field_type === "Select") {
    return field.select_options?.map(option => ({ label: option, value: option })) || [];
  } else if (field.doctype_field_type === "Link") {
    return field.linked_records?.map(record => ({ label: record, value: record })) || [];
  }
  return [];
};

const submitLead = async () => {
  emitter.emit("lead_submission_started", lead.value);
  const leadData = JSON.parse(JSON.stringify(toRaw(lead.value)));
  // Convert objects to string values for "Select" and "Link" fields
  Object.keys(leadData).forEach((key) => {
    if (typeof leadData[key] === "object" && leadData[key] !== null) {
      leadData[key] = leadData[key].value || leadData[key].label || "";
    }
  });

  try {
    const response = await fetch("/api/method/frappe_whatsapp.api.whatsapp.save_as_lead", {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': csrfToken.value
      },
      method: "POST",
      body: JSON.stringify({ doctype: form_name.value, data: leadData }),
    });

    const result = await response.json();
    if (result.message.status === "success") {
      emitter.emit("lead_submission_completed", lead.value);
    } else {
      console.error("Error submitting lead:", result.message);
    }
  } catch (error) {
    console.error("Error submitting lead:", error);
  }
};

</script>
