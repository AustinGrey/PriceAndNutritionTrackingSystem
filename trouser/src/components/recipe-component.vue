<template>
    <div :class="$options.name">
        <site-button
                @click.native="$emit('delete')"
                :link-appearance="true"
                class="delete"
        >
            <fa-icon :icon="['fas', 'minus']"></fa-icon>
        </site-button>
        <site-button
                :id="`${id}:name`"
                @click.native="onClickNote"
                :link-appearance="true"
                class="name"
        >
            {{name}}<span v-show="wantsNote">*</span>
        </site-button>
        <input-unit
                :id="`${id}:amount`"
                v-model="syncedAmount"
                :units="availableUnits"
        />
<!--        <input-float-->
<!--                :id="`${id}:amount`"-->
<!--                class="amount"-->
<!--                :label='includeLabels ? "Amount" : ""'-->
<!--                :extra='{style:"min-width: 0;text-align: right"}'-->
<!--                v-model="syncedAmount"-->
<!--        />-->
<!--        <input-float-->
<!--                :id="`${id}:unit`"-->
<!--                class="unit"-->
<!--                type="select"-->
<!--                :label='includeLabels ? "Unit" : ""'-->
<!--                v-model="syncedUnit"-->
<!--                :hide-default-option="true"-->
<!--        >-->
<!--            <option value="weight">g</option>-->
<!--            <option value="servings">serving</option>-->
<!--        </input-float>-->

        <input-float
                :id="`${id}:note`"
                class="note"
                label="Note"
                hint="Information about this specific ingredient in this specific recipe"
                :multiline="true"
                v-show="hasNote"
                :extra='{class:{"resizable-vertical":true}}'
                v-model="syncedNote"
        />
    </div>
</template>

<script>
    import InputFloat from "@/components/inputs/input-float";
    import SiteButton from "@/components/inputs/site-button";
    import InputUnit from "@/components/inputs/input-unit";

    export default {
        name: "recipe-component",
        components: {InputUnit, SiteButton, InputFloat},
        props: {
            name: String,
            note: {
                type: String,
                default: ''
            },
            unit: String, // one of 'servings' or 'weight'
            amount: Number,
            type: String,
            recipe_or_ingredient_id: Number,
            id: Number,
            // g/ml (== g/cm^3). The density of the food this component is of.
            // If provided, the user will be able to pick volume units as well as mass units
            density: {
                type: Number
            },
            // g / 1 serving of this food
            servingSize: {
                type: Number
            },
            // Name for a typical serving
            servingSizeName: {
                type: String
            }
        },
        data() {
            return {
                // Internal data storage for user editable properties
                synced: {
                    unit: null,
                    amount: null,
                },
                // If the user has stated they wanted to add a note
                wantsNote: false
            }
        },
        mounted() {
            // Transfer synced props to internal data
            this.syncedNote = this.note || ''; //@todo is this necessary anymore?

            // Do this so that deleting the note text does not immediately hide the note box
            this.wantsNote = this.syncedNote !== '';
        },
        computed: {
            hasNote() {
                return this.syncedNote !== '' || this.wantsNote;
            },
            syncedNote: {
                get() {
                    return this.note;
                },
                set(value) {
                    this.$emit("update:note", value);
                }
            },
            syncedUnit: {
                get() {
                    return this.unit;
                },
                set(value) {
                    this.$emit("update:unit", value)
                }
            },
            syncedAmount: {
                get() {
                    return this.amount;
                },
                set(value) {
                    this.$emit("update:amount", parseFloat(value) || 0)
                }
            },
            /**
             * The units of measure that this component food can be in
             */
            availableUnits() {
                let units = {
                    kg: 1000,
                    g: 1,
                    mg: 0.001,
                    oz: 28.34952,
                };

                if(this.servingSize){
                    units[this.servingSizeName || "serving"] = this.servingSize;
                }

                if (this.density) {
                    let metricVolumeUnits = {
                        ml: 1,
                        l: 1000,
                        cup: 250 // Because apparently somehow the imperial system screwed up cups so bad they have 3 different versions of them in the US alone, the common wealth fixed it.
                    };
                    let usVolumeUnits = {
                        "cup (US legal)": 240,
                        "cup (US customary)": 236.5882365,
                        "fl.oz.": 29.5735295625,
                        "tbsp": 14.78676478125,
                        "tsp": 4.92892159375,
                        "pinch": 0.31 // Because now verbs are units... great
                    };
                    units = {
                        ...units,
                        ...Object.fromEntries(Object.entries(metricVolumeUnits).map(([k, v]) => [k, v * this.density])),
                        ...Object.fromEntries(Object.entries(usVolumeUnits).map(([k, v]) => [k, v * this.density]))
                    }
                }

                return units;
            }
        },
        methods: {
            onClickNote() {
                this.wantsNote = !this.wantsNote;
                this.syncedNote = '';

            }
        }
    }
</script>

<style scoped lang="scss">
    // @todo these styles dont really belong here, they should belong to the recipe manager, as a single component doesn't care about how it's positioned in a grid
    .recipe-component {
        display: contents;

        // Unwrap the input unit
        .input-unit{
            display: contents;
            &::v-deep >div{
                display: contents
            }
        }
    }
</style>