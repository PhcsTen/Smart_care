<template>
  <!-- ส่วนหัวแอปพลิเคชัน -->
  <AppBar @toggle-drawer="drawer = !drawer" />
  <v-main>
    <v-container>
      <!-- ปุ่มควบคุมหลัก -->
      <v-row class="align-center">
        <v-col cols="auto" class="pa-0">
          <v-btn color="red" @click="goBack" class="btn-back">
            <v-icon start>mdi-arrow-left</v-icon> กลับ
          </v-btn>
        </v-col>
        <v-col cols="auto" class="pa-0 ml-3">
          <v-btn color="success" @click="toggleStudent">
            <v-icon start>mdi-account-school-outline</v-icon>
            เพิ่มข้อมูลนักเรียน
          </v-btn>
        </v-col>
      </v-row>

      <div style="height: 24px"></div>

      <!-- ตารางแสดงข้อมูลนักเรียน -->
      <v-sheet rounded>
        <v-data-table
          :headers="headers"
          :items="students"
          :items-per-page="10"
          :search="search"
          class="custom-table custom-footer"
        >
          <!-- ส่วนหัวตาราง -->
          <template v-slot:top>
            <v-toolbar flat class="bg-success text-white">
              <v-toolbar-title>
                <v-icon
                  icon="mdi-account-school-outline"
                  size="x-small"
                  class="me-2"
                  color="white"
                />
                ตารางข้อมูลนักเรียน
              </v-toolbar-title>
              <v-spacer></v-spacer>
              <!-- ช่องค้นหา -->
              <v-text-field
                v-model="search"
                label="ค้นหา"
                clearable
                variant="outlined"
                hide-details
                density="compact"
                style="max-width: 300px"
              />
            </v-toolbar>
          </template>

          <!-- ส่วนหัวคอลัมน์ -->
          <template v-slot:header="{ headers }">
            <tr>
              <th
                v-for="header in headers"
                :key="header.key"
                style="background-color: #43a047; color: white"
              >
                {{ header.title }}
              </th>
            </tr>
          </template>

          <!-- ข้อมูลแต่ละแถว -->
          <template v-slot:item="{ item, index }">
            <tr
              :style="{
                backgroundColor: index % 2 === 0 ? '#e8f5e9' : '#ffffff',
              }"
            >
              <td style="color: black">{{ index + 1 }}</td>
              <td style="color: black">{{ item.student_code }}</td>
              <td style="color: black">{{ item.full_name }}</td>
              <td style="color: black">{{ item.nickname || "-" }}</td>
              <td style="color: black">{{ formatGender(item.gender) }}</td>
              <td style="color: black">
                {{ formatThaiDate(item.birth_date) }}
              </td>
              <td style="color: black">
                {{ calculateAge(item.birth_date) }}
              </td>
              <td style="color: black">
                {{ item.is_active ? "ศึกษาอยู่" : "จบแล้ว" }}
              </td>
              <!-- ปุ่มดู -->
              <td class="text-center">
                <v-avatar
                  color="green darken-2"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="viewStudent(item)"
                >
                  <v-icon
                    color="white"
                    icon="mdi-eye-arrow-right-outline"
                    size="20"
                  />
                </v-avatar>
              </td>
              <!-- ปุ่มแก้ไข -->
              <td class="text-center">
                <v-avatar
                  color="yellow darken-2"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="editStudent(item)"
                >
                  <v-icon color="white" icon="mdi-pencil" size="20" />
                </v-avatar>
              </td>
              <!-- ปุ่มลบ -->
              <td class="text-center">
                <v-avatar
                  color="red darken-1"
                  size="32"
                  class="elevation-1"
                  style="cursor: pointer"
                  @click="confirmRemove(item.student_id)"
                >
                  <v-icon color="white" icon="mdi-delete" size="20" />
                </v-avatar>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-sheet>
    </v-container>

    <!-- Dialog ยืนยันการลบผู้นักเรียน -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400">
      <v-card class="confirm-delete-dialog">
        <v-card-title class="text-h6 confirm-delete-title"
          >ยืนยันการลบ</v-card-title
        >
        <v-card-text class="confirm-delete-text"
          >คุณต้องการลบนักเรียนคนนี้ใช่หรือไม่?</v-card-text
        >
        <v-card-actions class="confirm-delete-actions">
          <v-spacer />
          <!-- ปุ่มยกเลิก -->
          <v-btn
            color="red-darken-1"
            variant="flat"
            class="text-white"
            @click="confirmDeleteDialog = false"
            >ยกเลิก</v-btn
          >
          <!-- ปุ่มยืนยันลบ -->
          <v-btn
            color="green-darken-1"
            variant="flat"
            class="text-white"
            @click="confirmDelete"
            >ลบ</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- ฟอร์มเพิ่ม/แก้ไขข้อมูลนักเรียน -->
    <v-dialog v-model="dialog" persistent max-width="850">
      <v-card style="background-color: #ffffff; color: black">
        <!-- หัวข้อฟอร์ม -->
        <v-toolbar flat :color="isEditing ? 'warning' : 'success'">
          <v-card-title class="text-white">
            {{ isEditing ? "แก้ไขข้อมูลนักเรียน" : "เพิ่มข้อมูลนักเรียน" }}
          </v-card-title>
        </v-toolbar>

        <v-card-text>
          <v-row>
            <!-- คำนำหน้า -->
            <v-col cols="12" sm="4">
              <v-select
                v-model="record.prefix_name"
                :items="['เด็กชาย', 'เด็กหญิง']"
                label="คำนำหน้า"
                variant="outlined"
                color="success"
                :rules="[required]"
              />
            </v-col>

            <!-- รหัสนักเรียน -->
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="record.student_code"
                label="รหัสนักเรียน"
                variant="outlined"
                color="success"
                :rules="[required, idStudent_code]"
              />
            </v-col>

            <!-- เลขบัตรประชาชน -->
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="record.id_card_number"
                label="เลขบัตรประชาชน"
                variant="outlined"
                color="success"
                :rules="[required, idCardRule]"
              />
            </v-col>

            <!-- ชื่อ -->
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="record.first_name"
                label="ชื่อ"
                variant="outlined"
                color="success"
                :rules="[required]"
              />
            </v-col>

            <!-- นามสกุล -->
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="record.last_name"
                label="นามสกุล"
                variant="outlined"
                color="success"
                :rules="[required]"
              />
            </v-col>

            <!-- ชื่อเล่น -->
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="record.nickname"
                label="ชื่อเล่น"
                variant="outlined"
                color="success"
              />
            </v-col>

            <!-- เพศ -->
            <v-col cols="12" sm="4">
              <v-select
                v-model="record.gender"
                :items="['ชาย', 'หญิง']"
                label="เพศ"
                variant="outlined"
                color="success"
              />
            </v-col>
            <!-- หมู่เลือด -->
            <v-col cols="12" sm="2">
              <v-select
                v-model="record.blood_group"
                :items="['A', 'B', 'AB', 'O']"
                label="หมู่เลือด"
                variant="outlined"
                color="success"
              />
            </v-col>
            <!-- วันเกิด -->
            <v-col cols="12" sm="5">
              <v-menu
                v-model="showDatePicker"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    :model-value="formatThaiDate(record.birth_date)"
                    label="วันเกิด"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    variant="outlined"
                    clearable
                    @click:clear="clearBirthDate"
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="birthDateModel"
                  @update:modelValue="handleDateSelect"
                  locale="th"
                  :first-day-of-week="0"
                  :max="new Date().toISOString().split('T')[0]"
                ></v-date-picker>
              </v-menu>
            </v-col>
            <!-- อายุ -->
            <v-col cols="12" sm="4">
              <v-text-field
                :value="
                  'อายุ' +
                  ' ' +
                  calculateAge(record.birth_date) +
                  (calculateAge(record.birth_date) ? '' : '')
                "
                readonly
                variant="outlined"
                color="success"
              />
            </v-col>
            <!-- สถานะการเรียน -->
            <v-col cols="12" sm="3">
              <v-checkbox
                v-model="record.is_active"
                label="สถานะศึกษาอยู่"
                :true-value="1"
                :false-value="0"
                color="success"
              />
            </v-col>

            <!-- ที่อยู่ตามทะเบียนบ้าน -->
            <v-col cols="12" sm="12">
              <v-card class="mb-2" variant="outlined">
                <v-card-title class="text-subtitle-1">
                  <v-icon icon="mdi-home-map-marker" class="mr-2"></v-icon>
                  ที่อยู่ตามทะเบียนบ้าน {{ record.selectedFullAddressPermanent }}
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" sm="12">
                      <v-text-field
                        v-model="record.permanant_address"
                        label="เลขที่"
                        variant="outlined"
                        color="success"
                      />
                    </v-col>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="selectedProvinceCodePermanent"
                        :items="provinces"
                        item-title="provinceNameTh"
                        item-value="provinceCode"
                        label="จังหวัด"
                        variant="outlined"
                        color="success"
                      />
                    </v-col>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="selectedDistrictCodePermanent"
                        :items="filteredDistrictsPermanent"
                        item-title="districtNameTh"
                        item-value="districtCode"
                        label="อำเภอ/เขต"
                        variant="outlined"
                        color="success"
                        :disabled="!selectedProvinceCodePermanent"
                      />
                    </v-col>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="selectedSubdistrictCodePermanent"
                        :items="filteredSubdistrictsPermanent"
                        item-title="subdistrictNameTh"
                        item-value="subdistrictCode"
                        label="ตำบล/แขวง"
                        variant="outlined"
                        color="success"
                        :disabled="!selectedDistrictCodePermanent"
                      />
                    </v-col>
                  </v-row>

                  <div class="text-center mt-2">
                    <div v-if="selectedFullAddressPermanent" class="mt-2">
                      ที่อยู่ที่เลือก: {{ selectedFullAddressPermanent }}
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- ที่อยู่ปัจจุบัน -->
            <v-col cols="12" sm="12">
              <v-card class="mb-2" variant="outlined">
                <v-card-title class="text-subtitle-1">
                  <v-icon icon="mdi-home-map-marker" class="mr-2"></v-icon>
                  ที่อยู่ปัจจุบัน {{ record.selectedFullAddressPresent }}
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" sm="12">
                      <v-text-field
                        v-model="record.present_address"
                        label="เลขที่"
                        variant="outlined"
                        color="success"
                      />
                    </v-col>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="selectedProvinceCodePresent"
                        :items="provinces"
                        item-title="provinceNameTh"
                        item-value="provinceCode"
                        label="จังหวัด"
                        variant="outlined"
                        color="success"
                      />
                    </v-col>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="selectedDistrictCodePresent"
                        :items="filteredDistrictsPresent"
                        item-title="districtNameTh"
                        item-value="districtCode"
                        label="อำเภอ/เขต"
                        variant="outlined"
                        color="success"
                        :disabled="!selectedProvinceCodePresent"
                      />
                    </v-col>
                    <v-col cols="12" sm="4">
                      <v-select
                        v-model="selectedSubdistrictCodePresent"
                        :items="filteredSubdistrictsPresent"
                        item-title="subdistrictNameTh"
                        item-value="subdistrictCode"
                        label="ตำบล/แขวง"
                        variant="outlined"
                        color="success"
                        :disabled="!selectedDistrictCodePresent"
                      />
                    </v-col>
                  </v-row>
                  <!-- ส่วนแสดงที่อยู่ที่เลือก -->
                  <div class="text-center mt-2">
                    <div v-if="selectedFullAddressPresent" class="mt-2">
                      ที่อยู่ที่เลือก: {{ selectedFullAddressPresent }}
                    </div>

                    <!-- เพิ่มปุ่มใช้ที่อยู่เดียวกับทะเบียนบ้าน -->
                    <v-btn
                      color="success"
                      variant="tonal"
                      @click="useSameAsPermanentAddress"
                      class="mt-2"
                      :disabled="!selectedFullAddressPermanent"
                    >
                      <v-icon icon="mdi-content-copy" class="mr-2"></v-icon>
                      ใช้ที่อยู่เดียวกับทะเบียนบ้าน
                    </v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- ส่วนพิกัดที่ตั้ง -->
            <v-col cols="12">
              <v-card class="mb-4" variant="outlined">
                <v-card-title class="text-subtitle-1">
                  <v-icon icon="mdi-map-marker" class="mr-2"></v-icon>
                  พิกัดที่ตั้ง
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <!-- ละติจูด -->
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="record.latitude"
                        label="ละติจูด (Latitude)"
                        variant="outlined"
                        color="success"
                        type="number"
                        step="0.000001"
                        :rules="[latitudeRule]"
                      />
                    </v-col>
                    <!-- ลองติจูด -->
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="record.longitude"
                        label="ลองติจูด (Longitude)"
                        variant="outlined"
                        color="success"
                        type="number"
                        step="0.000001"
                        :rules="[longitudeRule]"
                      />
                    </v-col>
                  </v-row>
                  <div class="text-center mt-2">
                    <!-- ปุ่มเปิดแผนที่ -->
                    <v-btn
                      color="success"
                      variant="tonal"
                      @click="openMapPicker"
                    >
                      <v-icon icon="mdi-map" class="mr-2"></v-icon>
                      เลือกตำแหน่งจากแผนที่
                    </v-btn>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- รูปภาพนักเรียน -->
            <v-col cols="12" sm="12">
              <v-file-input
                label="เลือกรูปภาพนักเรียน"
                accept="image/*"
                variant="outlined"
                color="success"
                prepend-icon="mdi-camera"
                @change="handleImageUpload"
                clearable
                @click:clear="removeImage"
              />

              <!-- แสดงภาพตัวอย่าง หากเลือกใหม่ -->
              <div v-if="imagePreview" class="mt-2 text-center">
                <v-img
                  :src="imagePreview"
                  max-width="250"
                  max-height="250"
                  class="mx-auto"
                  style="border-radius: 12px; border: 1px solid #ccc"
                />
              </div>

              <!-- แสดงภาพจากฐานข้อมูล หากยังไม่มี preview -->
              <div v-else-if="record?.student_photo" class="mt-2 text-center">
                <v-img
                  :src="getStudentImageUrl(record.student_photo)"
                  max-width="250"
                  max-height="250"
                  class="mx-auto"
                  style="border-radius: 12px; border: 1px solid #ccc"
                />
              </div>

              <!-- fallback ถ้าไม่มีภาพเลย -->
              <div v-else class="text-grey mt-2 text-center">
                ยังไม่มีรูปภาพ
              </div>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider></v-divider>

        <!-- ปุ่มควบคุมฟอร์ม -->
        <v-card-actions class="justify-end">
          <v-btn color="red darken-1" variant="flat" @click="dialog = false"
            >ยกเลิก</v-btn
          >
          <v-btn
            color="green darken-1"
            variant="flat"
            class="text-white ml-2"
            :disabled="!isStudentFormValid"
            @click="save"
            >บันทึก</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- กล่องโต้ตอบแผนที่ OpenLayers -->
    <v-dialog v-model="mapDialog" max-width="800" fullscreen>
      <v-card>
        <v-toolbar color="primary">
          <v-toolbar-title class="text-white">
            เลือกตำแหน่งบนแผนที่
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="mapDialog = false">
            <v-icon color="white">mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-text style="height: calc(100vh - 120px); padding: 0">
          <!-- องค์ประกอบแผนที่ OpenLayers -->
          <div
            ref="mapRef"
            id="map"
            style="width: 100%; height: 100%; position: relative"
          >
            <!-- ปุ่มสลับแผนที่ -->
            <v-btn
              icon
              class="map-toggle-btn"
              @click="toggleMapType"
              style="position: absolute; top: 10px; right: 10px; z-index: 999"
              :title="isSatellite ? 'Street View' : 'Satellite View'"
            >
              <v-icon>{{ isSatellite ? "mdi-map" : "mdi-earth" }}</v-icon>
            </v-btn>
          </div>
          <!-- แสดงพิกัดปัจจุบัน -->
          <div class="map-coordinate-display pa-2">
            <v-chip class="ma-1" color="primary">
              <v-icon start>mdi-crosshairs-gps</v-icon>
              ละติจูด: {{ mapLatitude?.toFixed(6) || "N/A" }}
            </v-chip>
            <v-chip class="ma-1" color="primary">
              <v-icon start>mdi-crosshairs-gps</v-icon>
              ลองติจูด: {{ mapLongitude?.toFixed(6) || "N/A" }}
            </v-chip>
          </div>
        </v-card-text>
        <v-card-actions class="justify-end">
          <!-- ปุ่มยกเลิก -->
          <v-btn color="red darken-1" variant="flat" @click="mapDialog = false">
            ยกเลิก
          </v-btn>
          <!-- ปุ่มยืนยันตำแหน่ง -->
          <v-btn
            color="green darken-1"
            variant="flat"
            class="text-white ml-2"
            @click="confirmMapLocation"
            :disabled="!mapLatitude || !mapLongitude"
          >
            ยืนยันตำแหน่ง
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- แถบแจ้งเตือนสถานะ -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      timeout="1000"
      location="center"
      class="snackbar-fullscreen"
      transition="slide-y-transition"
    >
      <v-icon
        icon="mdi-alert-circle-outline"
        class="mr-2"
        size="large"
        color="white"
      />
      {{ snackbar.text }}
    </v-snackbar>
  </v-main>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRouter } from "vue-router";
import axios from "@/utils/axios"; // ใช้ instance แทน
import AppBar from "@/views/appbar/AppBar.vue";
import { API_BASE_URL } from "@/assets/config";

// นำเข้าไลบรารี OpenLayers
import "ol/ol.css";
import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import XYZ from "ol/source/XYZ";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import { fromLonLat, toLonLat } from "ol/proj";
import { defaults as defaultInteractions } from "ol/interaction";
import { Circle as CircleStyle, Fill, Stroke, Style } from "ol/style";
import Point from "ol/geom/Point";
import Feature from "ol/Feature";
import provinces from "@/assets/provinces.json";
import districts from "@/assets/districts.json";
import subdistricts from "@/assets/subdistricts.json";

//วันเกิด
// เพิ่มตัวแปรเหล่านี้
const showDatePicker = ref(false);
const birthDateModel = ref("");

// ฟังก์ชันจัดการเมื่อเลือกวันที่
const handleDateSelect = (date) => {
  if (date) {
    record.value.birth_date = date;
    birthDateModel.value = date;
  }
  showDatePicker.value = false;
};

// ฟังก์ชันล้างวันที่
const clearBirthDate = () => {
  record.value.birth_date = "";
  birthDateModel.value = "";
};

// ฟังก์ชันจัดรูปแบบวันที่ไทย
const formatThaiDate = (dateInput) => {
  if (!dateInput) return "";

  try {
    const date = new Date(dateInput); // แปลงให้เป็น Date object ถ้าไม่ใช่

    const thaiDays = [
      "อาทิตย์",
      "จันทร์",
      "อังคาร",
      "พุธ",
      "พฤหัสบดี",
      "ศุกร์",
      "เสาร์",
    ];
    const thaiMonths = [
      "มกราคม",
      "กุมภาพันธ์",
      "มีนาคม",
      "เมษายน",
      "พฤษภาคม",
      "มิถุนายน",
      "กรกฎาคม",
      "สิงหาคม",
      "กันยายน",
      "ตุลาคม",
      "พฤศจิกายน",
      "ธันวาคม",
    ];

    const day = thaiDays[date.getDay()];
    const dayOfMonth = date.getDate();
    const month = thaiMonths[date.getMonth()];
    const year = date.getFullYear() + 543;

    return `${day}ที่ ${dayOfMonth} ${month} ${year}`;
  } catch {
    return dateInput;
  }
};

// ฟังก์ชันคำนวณอายุใหม่
const calculateAge = (dateInput) => {
  if (!dateInput) return "";

  try {
    let birthDate;

    // ถ้าเป็น string ภาษาไทย เช่น "อาทิตย์ที่ 1 มกราคม 2565"
    if (typeof dateInput === "string" && dateInput.includes("ที่")) {
      const parts = dateInput.split(" ");
      const day = parseInt(parts[1].replace("ที่", ""), 10);
      const month = parts[2];
      const year = parseInt(parts[3], 10) - 543; // แปลงปีไทยเป็น ค.ศ.

      const thaiMonths = [
        "มกราคม",
        "กุมภาพันธ์",
        "มีนาคม",
        "เมษายน",
        "พฤษภาคม",
        "มิถุนายน",
        "กรกฎาคม",
        "สิงหาคม",
        "กันยายน",
        "ตุลาคม",
        "พฤศจิกายน",
        "ธันวาคม",
      ];
      const monthIndex = thaiMonths.indexOf(month);
      if (monthIndex === -1) return "";

      birthDate = new Date(year, monthIndex, day);
    } else {
      // ถ้าเป็น Date object หรือ ISO string
      birthDate = new Date(dateInput);
      if (isNaN(birthDate.getTime())) return "";
    }

    const today = new Date();

    let years = today.getFullYear() - birthDate.getFullYear();
    let months = today.getMonth() - birthDate.getMonth();
    const days = today.getDate() - birthDate.getDate();

    if (days < 0) {
      months--; // วันยังไม่ถึงในเดือนนี้
    }

    if (months < 0) {
      years--;
      months += 12;
    }

    return `${years} ปี ${months} เดือน`;
  } catch (error) {
    console.error("Error calculating age:", error);
    return "";
  }
};

// สำหรับที่อยู่ทะเบียนบ้าน
const selectedProvinceCodePermanent = ref(null);
const selectedDistrictCodePermanent = ref(null);
const selectedSubdistrictCodePermanent = ref(null);

// สำหรับที่อยู่ปัจจุบัน
const selectedProvinceCodePresent = ref(null);
const selectedDistrictCodePresent = ref(null);
const selectedSubdistrictCodePresent = ref(null);

// filter อำเภอจากจังหวัด (ทะเบียนบ้าน)
const filteredDistrictsPermanent = computed(() =>
  districts.filter(
    (d) => d.provinceCode === selectedProvinceCodePermanent.value
  )
);

// filter ตำบลจากอำเภอ (ทะเบียนบ้าน)
const filteredSubdistrictsPermanent = computed(() =>
  subdistricts.filter(
    (s) => s.districtCode === selectedDistrictCodePermanent.value
  )
);

// filter อำเภอจากจังหวัด (ปัจจุบัน)
const filteredDistrictsPresent = computed(() =>
  districts.filter((d) => d.provinceCode === selectedProvinceCodePresent.value)
);

// filter ตำบลจากอำเภอ (ปัจจุบัน)
const filteredSubdistrictsPresent = computed(() =>
  subdistricts.filter(
    (s) => s.districtCode === selectedDistrictCodePresent.value
  )
);

// ที่อยู่ทะเบียนบ้านที่รวมจากการเลือก
const selectedFullAddressPermanent = computed(() => {
  const province = provinces.find(
    (p) => p.provinceCode === selectedProvinceCodePermanent.value
  );
  const district = districts.find(
    (d) => d.districtCode === selectedDistrictCodePermanent.value
  );
  const subdistrict = subdistricts.find(
    (s) => s.subdistrictCode === selectedSubdistrictCodePermanent.value
  );
  const postalCode = subdistrict?.postalCode || "";

  const address = record.value.permanant_address?.trim() || "";

  return [
    address,
    subdistrict?.subdistrictNameTh,
    district?.districtNameTh,
    province?.provinceNameTh,
    postalCode,
  ]
    .filter(Boolean)
    .join(" ");
});

// ที่อยู่ปัจจุบันที่รวมจากการเลือก
const selectedFullAddressPresent = computed(() => {
  const province = provinces.find(
    (p) => p.provinceCode === selectedProvinceCodePresent.value
  );
  const district = districts.find(
    (d) => d.districtCode === selectedDistrictCodePresent.value
  );
  const subdistrict = subdistricts.find(
    (s) => s.subdistrictCode === selectedSubdistrictCodePresent.value
  );
  const postalCode = subdistrict?.postalCode || "";

  const address = record.value.present_address?.trim() || "";

  return [
    address,
    subdistrict?.subdistrictNameTh,
    district?.districtNameTh,
    province?.provinceNameTh,
    postalCode,
  ]
    .filter(Boolean)
    .join(" ");
});

// ใช้ที่อยู่ทะเบียนบ้านเป็นที่อยู่ปัจจุบัน
const useSameAsPermanentAddress = () => {
  record.value.present_address = record.value.permanant_address;
  selectedProvinceCodePresent.value = selectedProvinceCodePermanent.value;
  selectedDistrictCodePresent.value = selectedDistrictCodePermanent.value;
  selectedSubdistrictCodePresent.value = selectedSubdistrictCodePermanent.value;
};

// เพิ่มตัวแปรเหล่านี้
const imagePreview = ref(null);
const selectedImageFile = ref(null);

// ฟังก์ชันจัดการการอัพโหลดรูปภาพ
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedImageFile.value = file;

    // สร้าง URL สำหรับแสดงภาพตัวอย่าง
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  } else {
    imagePreview.value = null;
    selectedImageFile.value = null;
  }
};

// ฟังก์ชันลบรูปภาพ
const removeImage = () => {
  imagePreview.value = null;
  selectedImageFile.value = null;
  // ล้างค่า input file ด้วย
  document.querySelector('input[type="file"]').value = "";
};

// ฟังก์ชันโหลดรูปภาพ
const getStudentImageUrl = (filename) => {
  if (!filename) return "";
  return `${API_BASE_URL}/uploads/${filename}`; // เปลี่ยน URL ตามจริง
};

// เมื่อโหลดข้อมูลนักเรียนสำหรับแก้ไข
const editStudent = (student) => {
  isEditing.value = true;
  record.value = { ...student };

  // แยกเลขที่ออกจาก present_address
  if (student.present_address) {
    selectedFullAddressPresent.value = record.value.present_address ;
  }

  // แยกเลขที่ออกจาก permanent_address
  if (student.permanent_address) {
    selectedFullAddressPermanent.value =  student.permanent_address;
  }

  // ตั้งค่าวันเกิด
  if (student.birth_date) {
    birthDateModel.value = student.birth_date.includes("T")
      ? student.birth_date.split("T")[0]
      : student.birth_date;
  }

  dialog.value = true;
};


// เพิ่มตัวแปร ref
const isSatellite = ref(false); // ค่าเริ่มต้น = street map
let baseLayer = null;

// แหล่งดาวเทียม (ใช้ OpenTopoMap / หรือเปลี่ยนเป็น Google/ESRI ได้)
const satelliteSource = new XYZ({
  //url:  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  //attributions: "© ArcgisMap",
  url: "http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}",
  attributions: "© GoogleMap Hybrid",
});

// ฟังก์ชันสลับแผนที่
const toggleMapType = () => {
  isSatellite.value = !isSatellite.value;

  const newSource = isSatellite.value ? satelliteSource : new OSM();

  baseLayer.setSource(newSource);
};

// ตัวแปร Router
const router = useRouter();

// ตัวแปร UI
const drawer = ref(true); // สำหรับเปิด/ปิดเมนู
const dialog = ref(false); // ควบคุมการแสดงฟอร์ม
const isEditing = ref(false); // ตรวจสอบว่าเป็นการแก้ไขหรือเพิ่ม
const search = ref(""); // สำหรับค้นหาในตาราง
const mapDialog = ref(false); // ควบคุมการแสดงแผนที่
const mapLatitude = ref(null); // เก็บค่าละติจูดจากแผนที่
const mapLongitude = ref(null); // เก็บค่าลองติจูดจากแผนที่
const mapRef = ref(null); // สำหรับโหลดแผนที่

// ข้อมูลนักเรียน
const students = ref([]);

// Snackbar สำหรับแสดงข้อความแจ้งเตือน
const snackbar = ref({
  show: false,
  text: "",
  color: "success",
});

// ตัวแปรสำหรับการยืนยันการลบ
const confirmDeleteDialog = ref(false);
const deleteId = ref(null);

// ฟอร์มข้อมูลนักเรียน
const record = ref({
  student_id: null,
  id_card_number: "",
  student_code: "",
  prefix_name: "",
  first_name: "",
  last_name: "",
  nickname: "",
  gender: "",
  birth_date: "",
  age_range: "",
  present_address: "",
  permanant_address: "",
  latitude: null, // ละติจูด
  longitude: null, // ลองติจูด
  is_active: 0, // ค่าเริ่มต้น
  blood_group: "",
  postal_code: "",
});

// reset ฟอร์มข้อมูลนักเรียน
const resetForm = () => {
  record.value = {
    student_id: null,
    id_card_number: "",
    student_code: "",
    prefix_name: "",
    first_name: "",
    last_name: "",
    nickname: "",
    gender: "",
    birth_date: "",
    age_range: "",
    present_address: "",
    permanant_address: "",
    latitude: null,
    longitude: null,
    is_active: "0",
    blood_group: "",
    postal_code: "",
    student_photo: "",
  };

  // รีเซตค่าภาพ preview ด้วย
  imagePreview.value = null;

  // รีเซตค่าจังหวัด/อำเภอ/ตำบล ถ้ามี
  selectedProvinceCodePermanent.value = null;
  selectedDistrictCodePermanent.value = null;
  selectedSubdistrictCodePermanent.value = null;

  selectedProvinceCodePresent.value = null;
  selectedDistrictCodePresent.value = null;
  selectedSubdistrictCodePresent.value = null;

  // รีเซต v-model อื่น ๆ ที่เกี่ยวข้อง (ถ้ามี)
};

// หัวคอลัมน์ตาราง
const headers = [
  { title: "ลำดับ", key: "index" },
  { title: "รหัสนักเรียน", key: "student_code" },
  { title: "ชื่อ-สกุล", key: "full_name" },
  { title: "ชื่อเล่น", key: "nickname" },
  { title: "เพศ", key: "gender" },
  { title: "วันเกิด", key: "birth_date" },
  { title: "ช่วงอายุ", key: "age_range" },
  { title: "สถานะ", key: "is_active" },
  { title: "ดู", key: "view", align: "center" },
  { title: "แก้ไข", key: "edit", align: "center" },
  { title: "ลบ", key: "delete", align: "center" },
];

// ตัวแปร OpenLayers
let map = null; // ตัวแปรเก็บออบเจ็กต์แผนที่
let markerSource = null; // แหล่งข้อมูลสำหรับ marker
let marker = null; // ตัว marker บนแผนที่

// กฎการตรวจสอบความถูกต้อง
const required = (v) => !!v || "จำเป็นต้องกรอก";
const idCardRule = (v) => (v && v.length === 13) || "ต้องมี 13 หลัก";
const idStudent_code = (v) => (v && v.length === 4) || "ต้องมี 4 หลัก";
const latitudeRule = (v) => {
  if (!v) return true;
  const num = parseFloat(v);
  return (num >= -90 && num <= 90) || "ค่าละติจูดต้องอยู่ระหว่าง -90 ถึง 90";
};
const longitudeRule = (v) => {
  if (!v) return true;
  const num = parseFloat(v);
  return (
    (num >= -180 && num <= 180) || "ค่าลองติจูดต้องอยู่ระหว่าง -180 ถึง 180"
  );
};

// ตรวจสอบความถูกต้องของฟอร์ม
const isStudentFormValid = computed(() => {
  const r = record.value;
  return (
    r.student_code &&
    r.id_card_number &&
    r.prefix_name &&
    r.first_name &&
    r.last_name
  );
});

// ฟังก์ชันสำหรับโหลดข้อมูลนักเรียน
const fetchStudents = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const response = await axios.get(`${API_BASE_URL}/students_all`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    const data = response.data.students || [];

    console.log("✅ ข้อมูลที่ได้จาก backend:", data);

    students.value = data.map((t) => ({
      ...t,
      full_name: `${t.prefix_name || ""}${t.first_name || ""} ${
        t.last_name || ""
      }`,
    }));

    // 👉 ถ้ามีนักเรียนคนแรก ให้เซ็ตที่อยู่
    if (data.length > 0) {
      selectedFullAddressPermanent.value = data[0].permanent_address || "";
      selectedFullAddressPresent.value = data[0].present_address || "";
    }
  } catch (error) {
    console.error("❌ โหลดข้อมูลนักเรียนล้มเหลว", error);
    showSnackbar("เกิดข้อผิดพลาดในการโหลดข้อมูลนักเรียน", "error");
  }
};

// จัดรูปแบบเพศสำหรับแสดงผล
const formatGender = (gender) => {
  return gender === "ชาย" ? "ชาย" : gender === "หญิง" ? "หญิง" : "-";
};

// ฟังก์ชันสำหรับเปิดแผนที่เลือกตำแหน่ง
const openMapPicker = () => {
  mapLatitude.value = record.value.latitude || 13.736717; // ค่าเริ่มต้นที่กรุงเทพ
  mapLongitude.value = record.value.longitude || 100.523186;
  mapDialog.value = true;

  // รอให้ DOM อัพเดทก่อนเริ่มต้นแผนที่
  nextTick(() => {
    if (!map) {
      initMap();
    } else {
      map.setTarget(mapRef.value);
      map.updateSize();
      // อัพเดทตำแหน่ง marker ถ้ามีค่าพิกัดอยู่แล้ว
      if (mapLatitude.value && mapLongitude.value) {
        const coordinate = fromLonLat([mapLongitude.value, mapLatitude.value]);
        updateMarker(coordinate);
        map.getView().setCenter(coordinate);
      }
    }
  });
};

// ฟังก์ชันเริ่มต้นแผนที่ OpenLayers
const initMap = () => {
  // สร้างแหล่งข้อมูลสำหรับ marker
  markerSource = new VectorSource();

  // สไตล์ของ marker
  const markerStyle = new Style({
    image: new CircleStyle({
      radius: 8,
      fill: new Fill({ color: "red" }),
      stroke: new Stroke({ color: "white", width: 2 }),
    }),
  });

  // ชั้นข้อมูล marker
  const markerLayer = new VectorLayer({
    source: markerSource,
    style: markerStyle,
  });

  // สร้างแผนที่
  baseLayer = new TileLayer({
    source: new OSM(),
  });

  map = new Map({
    target: "map",
    layers: [
      baseLayer,
      markerLayer, // จากเดิม
    ],
    view: new View({
      center: fromLonLat([100.523186, 13.736717]),
      zoom: 12,
    }),
    interactions: defaultInteractions(),
  });

  // เพิ่มเหตุการณ์เมื่อคลิกบนแผนที่
  map.on("click", (evt) => {
    const coordinate = evt.coordinate;
    const lonLat = toLonLat(coordinate);

    // อัพเดทค่าพิกัด
    mapLatitude.value = lonLat[1];
    mapLongitude.value = lonLat[0];

    // อัพเดทตำแหน่ง marker
    updateMarker(coordinate);
  });

  // ถ้ามีค่าพิกัดอยู่แล้ว ให้แสดง marker
  if (mapLatitude.value && mapLongitude.value) {
    const coordinate = fromLonLat([mapLongitude.value, mapLatitude.value]);
    updateMarker(coordinate);
    map.getView().setCenter(coordinate);
  }
};

// อัพเดทตำแหน่ง marker บนแผนที่
const updateMarker = (coordinate) => {
  // ลบ marker เดิม
  markerSource.clear();

  // สร้าง marker ใหม่
  marker = new Feature({
    geometry: new Point(coordinate),
  });

  // เพิ่ม marker ลงในแหล่งข้อมูล
  markerSource.addFeature(marker);
};
// ยืนยันตำแหน่งที่เลือกจากแผนที่
const confirmMapLocation = () => {
  record.value.latitude = mapLatitude.value;
  record.value.longitude = mapLongitude.value;
  mapDialog.value = false;
};

// เปิดฟอร์มเพิ่มนักเรียน
const toggleStudent = () => {
  resetForm();
  isEditing.value = false;
  dialog.value = true;
};

// ยืนยันการลบนักเรียน
const confirmRemove = (id) => {
  deleteId.value = id;
  confirmDeleteDialog.value = true;
};

// ลบนักเรียน
const confirmDelete = async () => {
  try {
    const token = localStorage.getItem("access_token");
    await axios.delete(`${API_BASE_URL}/student/delete/${deleteId.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    students.value = students.value.filter(
      (s) => s.student_id !== deleteId.value
    );
    showSnackbar("ลบนักเรียนสำเร็จ!", "success");
  } catch (error) {
    showSnackbar("เกิดข้อผิดพลาดในการลบนักเรียน", "error");
    console.error("Error deleting student:", error);
  } finally {
    confirmDeleteDialog.value = false;
  }
};

// บันทึกข้อมูลนักเรียน
const save = async () => {
  try {
    const token = localStorage.getItem("access_token");
    const payload = {
      student_id: record.value.student_id,
      id_card_number: record.value.id_card_number,
      student_code: record.value.student_code,
      prefix_name: record.value.prefix_name,
      first_name: record.value.first_name,
      last_name: record.value.last_name,
      nickname: record.value.nickname,
      gender: record.value.gender,
      birth_date: record.value.birth_date,
      age_range: calculateAge(record.value.birth_date), // ✅ แก้จุดนี้

      is_active: record.value.is_active,

      present_address: selectedFullAddressPresent.value, // ที่อยู่ปัจจุบัน
      permanent_address: selectedFullAddressPermanent.value, // ที่อยู่ตามทะเบียนบ้าน

      latitude: record.value.latitude,
      longitude: record.value.longitude,

      blood_group: record.value.blood_group,
      image: imagePreview.value, // ถ้า backend รอรับเป็น 'image'
    };
    const config = {
      headers: {
        "Content-Type": "application/json", // ✅ สำคัญ
        Authorization: `Bearer ${token}`,
      },
    };
    //console.log("📌 ค่าที่จะส่งไป:", record.value.is_active);
    //console.log("image:", imagePreview.value);
    //console.log("present_address:", selectedFullAddressPresent.value);
    //console.log("permanent_address:", selectedFullAddressPermanent.value);
    //console.log("เตรียมข้อมูล :", payload);
    if (isEditing.value) {
      await axios.put(
        `${API_BASE_URL}/student/update/${payload.student_id}`,
        payload,
        config
      );
      showSnackbar("อัปเดตข้อมูลนักเรียนสำเร็จ!", "success");
      toggleStudent();
    } else {
      await axios.post(`${API_BASE_URL}/student/insert`, payload, config);
      showSnackbar("เพิ่มผู้ใช้สำเร็จ!", "success");
    }

    dialog.value = false;
    fetchStudents(); // โหลดข้อมูลใหม่
  } catch (error) {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      router.push("/login");
    } else {
      console.error("บันทึกข้อมูลไม่สำเร็จ", error);
      showSnackbar("เกิดข้อผิดพลาดในการบันทึกข้อมูล", "error");
    }
  }
};

// แสดงข้อความแจ้งเตือน
const showSnackbar = (message, type = "success") => {
  snackbar.value.text = message;
  snackbar.value.color = type;
  snackbar.value.show = true;
};

// เมื่อคอมโพเนนต์ถูกเมานต์
onMounted(() => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    router.push("/login");
    return;
  }
  fetchStudents();
});

// เมื่อคอมโพเนนต์จะถูกทำลาย
onBeforeUnmount(() => {
  if (map) {
    map.setTarget(undefined); // ล้างการอ้างอิงแผนที่
    map = null;
  }
});

// กลับไปหน้าเดิม
const goBack = () => {
  router.push("/home");
};
</script>

<style scoped>
/* สไตล์สำหรับแสดงพิกัดบนแผนที่ */
.map-coordinate-display {
  position: absolute;
  bottom: 55px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  z-index: 999;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-wrap: wrap;
}

/* สไตล์สำหรับปุ่มใช้ที่อยู่เดียวกัน */
.same-address-btn {
  margin-top: 12px;
  margin-bottom: 8px;
}

/* สไตล์สำหรับปุ่มลบรูปภาพ */
.image-delete-btn {
  margin-top: 8px;
}

/* สไตล์สำหรับกรอบรูปภาพ */
.image-preview {
  border-radius: 12px;
  border: 1px solid #ccc;
  padding: 4px;
  background-color: #f5f5f5;
}

/* ในส่วน style */
.v-menu__content {
  z-index: 2000 !important;
}

.v-date-picker {
  border-radius: 8px;
  overflow: hidden;
}

.v-date-picker-header {
  background-color: #43a047;
  color: white;
}

.v-date-picker-title {
  color: white !important;
}

.v-date-picker-controls button {
  color: white !important;
}
</style>
