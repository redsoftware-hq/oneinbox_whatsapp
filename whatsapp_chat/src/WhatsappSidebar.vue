<template>
  <div class="h-full w-100 bg-white flex flex-col border-r border-gray-100">
    <!-- Header -->
    <div class="p-4 flex justify-between items-center border-b bg-gray-100">
      <h2 class="text-lg font-semibold text-gray-700">Contacts</h2>
    </div>

    <!-- Search Bar -->
    <div class="p-2 bg-gray-100">
      <input
        v-model="search"
        type="text"
        placeholder="Search contacts..."
        class="w-full p-2 rounded-md border border-gray-300 focus:outline-none focus:ring focus:ring-blue-300"
      />
    </div>

    <div
      ref="scrollContainer"
      class="flex-1 overflow-y-auto min-h-0"
      @scroll="handleScroll"
    >
      <ul v-if="contacts.length">
        <li
          v-for="contact in contacts"
          :key="contact.phone"
          class="flex items-center justify-between p-4 cursor-pointer transition duration-200 hover:bg-gray-100 border-b border-gray-300 bg-white w-full"
          :class="{ 'bg-blue-100': selectedContact === contact.phone }"
          @click="selectContact(contact)"
        >
          <div class="flex flex-col w-full h-full">
            <div class="flex justify-between w-full">
              <div class="text-lg font-medium text-gray-800">
                {{ contact.phone }}
              </div>
              <Badge
                v-if="contact.unread_message_count > 0"
                variant="solid"
                theme="green"
                size="sm"
              >
                {{ contact.unread_message_count }}
              </Badge>
            </div>

            <div class="flex justify-between w-full">
              <div class="text-sm font-medium text-gray-800">
                {{ contact.whatsapp_name || "Unknown" }}
              </div>
              <div class="text-sm font-medium text-gray-400">
                {{ formatDate(contact.last_message_time) }}
              </div>
            </div>
          </div>
        </li>
      </ul>

      <!-- No Contacts Found -->
      <div v-else class="text-gray-500 text-center p-4">
        No contacts found
      </div>

      <!-- Loading Indicator -->
      <div v-if="loadingMore" class="text-center p-2 text-gray-500">
        Loading more contacts...
      </div>
    </div>
  </div>
</template>

<script>
import { Badge } from "frappe-ui";
import { format, isToday, isYesterday } from "date-fns";
import { emitter } from "./utils/eventBus.js";
import { ref, watch, onMounted } from "vue";

export default {
  name: "WhatsappSidebar",

  props: {
    user_update: Boolean,
    socket: Object,
    csrfToken: String,
  },

  setup(props) {
    const search = ref("");
    const selectedContact = ref(null);
    const contacts = ref([]);
    const scrollContainer = ref(null);
    const loadingMore = ref(false);
    let page = 0;
    const pageSize = 20;
    let debounceTimer = null;

    const fetchContacts = async (searchTerm = "") => {
      if (loadingMore.value) return;
      loadingMore.value = true;
      try {
        const response = await fetch(
          `/api/method/frappe_whatsapp.api.whatsapp.get_whatsapp_contact?start=${page * pageSize}&page_length=${pageSize}&search_term=${encodeURIComponent(searchTerm)}`,
          {
            headers: { "X-Frappe-CSRF-Token": props.csrfToken },
          }
        );
        const data = await response.json();
        if (page === 0) {
          contacts.value = data.message || []; // Replace contacts on new search
        } else {
          contacts.value = [...contacts.value, ...(data.message || [])]; // Append contacts on scroll
        }
        page++;
      } catch (error) {
        console.error("Error fetching contacts:", error);
      } finally {
        loadingMore.value = false;
      }
    };

    const handleScroll = () => {
      if (debounceTimer) clearTimeout(debounceTimer);

      debounceTimer = setTimeout(() => {
        if (!scrollContainer.value || loadingMore.value) return;
        const { scrollTop, scrollHeight, clientHeight } = scrollContainer.value;
        if (scrollTop + clientHeight >= scrollHeight - 10) {
          fetchContacts(search.value);
        }
      }, 300);
    };

    watch(search, (newSearch) => {
      page = 0; // Reset pagination when search changes
      contacts.value = []; // Clear current contacts
      fetchContacts(newSearch); // Fetch new results based on search term
    });

    const selectContact = (contact) => {
      selectedContact.value = contact.phone;
      emitter.emit("contact-selected", {
        number: contact.phone,
        name: contact.whatsapp_name,
      });
      localStorage.setItem("selectedContact", JSON.stringify(contact));
      emitter.emit("contact-selected-refresh");
    };

    onMounted(() => {
      fetchContacts();
      if (props.socket) {
        props.socket.on("whatsapp_contact_update", (data) => {
          const existingIndex = contacts.value.findIndex((c) => c.phone === data.phone);

          if (!data.changed_fields || data.changed_fields.length === 0) {
            return;
          }

          if (existingIndex !== -1) {
            const existingContact = contacts.value[existingIndex];
            contacts.value.splice(existingIndex, 1);
            contacts.value.unshift({ ...existingContact, ...data });
          } else {
            contacts.value.unshift(data);
          }

          contacts.value = [...contacts.value];
        });
      }
    });

    const formatDate = (dateString) => {
      if (!dateString) return "";
      const lastInteraction = new Date(dateString);
      let formattedTime = "";
      const currentYear = new Date().getFullYear();
      const messageYear = lastInteraction.getFullYear();
      if (isToday(lastInteraction)) {
        formattedTime = format(lastInteraction, "hh:mm a");
      } else if (isYesterday(lastInteraction)) {
        formattedTime = "Yesterday";
      } else if (currentYear === messageYear) {
        formattedTime = format(lastInteraction, "dd MMM");
      } else {
        formattedTime = format(lastInteraction, "dd/MM/yy");
      }
      return formattedTime;
    };

    return {
      search,
      selectedContact,
      contacts,
      selectContact,
      formatDate,
      scrollContainer,
      handleScroll,
      loadingMore,
    };
  },
};
</script>
