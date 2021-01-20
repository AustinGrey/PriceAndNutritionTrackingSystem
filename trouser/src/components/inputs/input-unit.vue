<!--
Creates an input with an adjustable unit as one single control. If conversion data is specified,
adjusting the unit will also automatically convert the input amount

While other inputs are more general, this one is limited to being a number to help in conversion.
-->
<template>
    <div :class="$options.name">
        <div>
            <input-float
                    class="amount"
                    :id="id"
                    v-model="displayValue"
            />
            <input-float
                    class="unit"
                    :id="`${id}:unit`"
                    type="select"
                    v-model="displayUnit"
            >
                <option v-for="unit in Object.keys(normalizedUnits)" :key="unit" :value="unit">{{unit}}</option>
            </input-float>
        </div>
    </div>
</template>

<script>
    import InputFloat from "@/components/inputs/input-float";

    export default {
        name: "input-unit",
        components: {InputFloat},
        props: {
            // The id to use for the inputs
            id: {
                type: String,
                required: true
            },
            // The label for this input
            label: {
                type: String
            },
            // Which unit of the units dictionary is the primary one. Any conversion data should specify how to convert
            // to this unit. (e.g. 'g'). No matter what unit is currently chosen by the user or displayed, the reported
            // value of this component will be in this unit.
            primaryUnit: {
                type: String,
                required: true
            },
            // Describe what units are available for this value.
            // If a string, then the unit will be set directly, and the user will have no control
            // If an array, the user will have the ability to pick from amoung the provided units, but no automatic conversion will happen
            // If an object, the keys should be units and the values should be ratios describing how many of the primary unit is in 1 of the given unit
            // E.g. {'g': 1, 'mg': 0.001, 'kg': 1000}
            // If not specified, then the primary unit will be considered as if passed as a string here.
            units: {
                type: [Object, Array, String],
                required: false
            },
            // The current value of this input. In primary units
            value: {
                type: Number,
            }
        },
        data() {
            return {

                /**
                 * The currently displayed unit. Affects the display value
                 */
                displayUnit: this.primaryUnit
            }
        },
        computed: {
            displayValue: {
                /**
                 * The currently displayed value, based on the display unit
                 * @returns {Number}
                 */
                get() {
                    return this.convertUnits(this.value, this.primaryUnit, this.displayUnit);
                },
                set(value) {
                    this.$emit('input', this.convertUnits(parseFloat(value) || 0, this.displayUnit, this.primaryUnit));
                }
            },
            /**
             * Returns a units dictionary, even if the units passed in was an array or string
             * @returns {object}
             */
            normalizedUnits() {
                if (typeof this.units === 'string') return {[this.units]: 1};
                if (Array.isArray(this.units)) return this.units.reduce((output, unit) => {
                    output[unit] = 1;
                    return output
                }, {});
                return this.units;
            }
        },
        methods: {
            /**
             * Converts the given value that is in inUnits, to a value that is in outUnits
             * @param {number} value The value given in inUnits
             * @param {string} inUnit The unit the value starts out in, must exist in the normalizedUnits dictionary
             * @param {string} outUnit The unit the return value is in, must exist in the normalizedUnits dictionary
             * @returns {number}
             */
            convertUnits(value, inUnit, outUnit) {
                // Get the ratio of the current unit
                var inRatio = this.normalizedUnits[inUnit];
                var outRatio = this.normalizedUnits[outUnit];
                return (value * inRatio) / outRatio
            }
        }
    }
</script>

<style scoped lang="scss">
    .input-unit {
        >div{
            display: flex;
            align-items: baseline;

            .amount {
                flex: 1;

                ::v-deep .field__input {
                    text-align: right;
                    border-top-right-radius: 0;
                    border-bottom-right-radius: 0;
                    border-right-width: 0;
                }
            }

            .unit {
                ::v-deep .field__input {
                    padding-left: 0;
                    appearance: none;

                    border-top-left-radius: 0;
                    border-bottom-left-radius: 0;
                    border-left-width: 0;
                }
            }
        }
    }

</style>