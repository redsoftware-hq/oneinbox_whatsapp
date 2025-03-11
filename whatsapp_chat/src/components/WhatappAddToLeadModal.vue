<template>
  <Dialog v-model="show" :options="{ title: `Add ${form_name}`, size: '2xl' }">
    <template #body-content>
      <form @submit.prevent="submitLead">
        <div
          v-for="(field, index) in dynamicFields"
          :key="index"
          class="p-2"
          :class="{ 'overflow-y-auto max-h-96': dynamicFields.length > 8 }"
        >
          <FormControl
            :type="mapInputType(field.doctype_field_type, field.lead_field_name)"
            :size="'sm'"
            :variant="'subtle'"
            :placeholder="field.lead_field_name"
            :label="formatLabel(field.lead_field_name)"
            v-model="lead[field.lead_field_name]"
            :options="getOptions(field)"
            :as="mapInputType(field.doctype_field_type, field.lead_field_name) === 'autocomplete' ? 'autocomplete' : null"
          />
        </div>
        <div class="mt-4 flex justify-end text-black">
          <button class="mr-2 px-4 py-2 bg-gray-300 rounded" type="button" @click="closeDialog">Cancel</button>
          <button class="px-4 py-2 bg-gray-700 text-white rounded" type="submit">Save Lead</button>
        </div>
      </form>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watchEffect, defineProps, defineEmits } from "vue";
import { FormControl, createResource } from "frappe-ui";
import { toRaw } from "vue";
import { emitter } from "../utils/eventBus";

const props = defineProps({
  contact_number: String,
  first_name: String,
  showAddLeadModal: Boolean, // Parent controls this
});

// const emit = defineEmits(["update:showAddLeadModal"]); // Allows v-model usage


const show = ref(props.showAddLeadModal);
const responseMessage = ref("");

const fieldMappingsResource = createResource({
  url: "/api/method/frappe_whatsapp.api.whatsapp.get_leadmapping_fields",
  auto: true,
});

const formDataResource = createResource({
  url: "/api/method/frappe_whatsapp.api.whatsapp.get_form_data",
  auto: true,
});

const executiveOptions = ref([]);
const centerOptions = ref([]);
const dynamicFields = ref([]);
const lead = ref({});
const form_name = ref("");

// Sync modal state with prop
watchEffect(() => {
  show.value = props.showAddLeadModal;
});

// Close dialog properly
const closeDialog = () => {
  show.value = false;
  // emit("update:showAddLeadModal", false);
};

// Fetch and set field data
watchEffect(() => {
  if (formDataResource.data?.message) {
    executiveOptions.value = formDataResource.data.message.executive?.map(exec => ({
      label: exec.fullname,
      value: exec.fullname,
    })) || [];

    centerOptions.value = formDataResource.data.message.center?.map(center => ({
      label: center.name,
      value: center.name,
    })) || [];
  }
});

watchEffect(() => {
  if (fieldMappingsResource.data?.field_mappings) {
    dynamicFields.value = fieldMappingsResource.data.field_mappings;
    form_name.value = fieldMappingsResource.data.mappings.lead_reference_doctype;
    
    lead.value = dynamicFields.value.reduce((acc, field) => {
      acc[field.lead_field_value] = field.lead_field_value === "source" ? "Whatsapp" : "";
      return acc;
    }, {});

    lead.value.contact_number = props.contact_number || "Dummy";
    lead.value.first_name = props.first_name || "123456";
    lead.value.created_on = new Date().toISOString().split('T')[0];
  }
});

// Map input types
const mapInputType = (doctypeFieldType, leadFieldValue) => {
  if (leadFieldValue === "created_on") return "text";
  const typeMap = {
    Data: "text",
    Phone: "tel",
    Date: "text",
    Select: "autocomplete",
    Link: "autocomplete",
  };
  return typeMap[doctypeFieldType] || "text";
};

// Format labels properly
const formatLabel = (key) => key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());

// Get field options
const getOptions = (field) => {
  if (field.doctype_field_type === "Select") {
    return field.select_options.map(option => ({ label: option, value: option }));
  } else if (field.doctype_field_type === "Link") {
    return field.linked_records.map(record => ({ label: record, value: record }));
  }
  return [];
};

// Submit lead data
const submitLead = async () => {
  emitter.emit("lead_submission_started", lead.value);
  const leadData = JSON.parse(JSON.stringify(toRaw(lead.value)));
  const doctype = JSON.parse(JSON.stringify(toRaw(form_name.value)));
  
  try {
    const response = await fetch("/api/method/frappe_whatsapp.api.whatsapp.save_as_lead", {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      method: "POST",
      body: JSON.stringify({ doctype, data: leadData }),
    });

    const result = await response.json();
    if(result.message.status === "error") {
      responseMessage.value = result.message;
      return;
    }
    else if(result.message.status === "success") {
      emitter.emit("lead_submission_completed", lead.value);
    }

    else {
      responseMessage.value = "Error submitting lead.";
    }
    // closeDialog(); // Close modal on success
  } catch (error) {
    console.error("Error submitting lead:", error);
  }
};
</script>
