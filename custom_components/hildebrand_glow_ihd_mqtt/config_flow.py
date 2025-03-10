"""Config flow for Hildebrand Glow IHD MQTT."""
import logging
import voluptuous as vol
import zoneinfo

from homeassistant.config_entries import (
    ConfigFlow,
    CONN_CLASS_LOCAL_PUSH,
    OptionsFlow,
)
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_TIME_ZONE_ELECTRICITY,
    CONF_TIME_ZONE_GAS,
    CONF_TOPIC_PREFIX,
    DEFAULT_DEVICE_ID,
    DEFAULT_TOPIC_PREFIX,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

class HildebrandGlowIHDMQTTConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_LOCAL_PUSH
    
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            device_id = user_input.get(CONF_DEVICE_ID)
            topic_prefix = user_input.get(CONF_TOPIC_PREFIX)
            time_zone_electricity = user_input.get(CONF_TIME_ZONE_ELECTRICITY)
            time_zone_gas = user_input.get(CONF_TIME_ZONE_GAS)

            await self.async_set_unique_id('{}_{}'.format(DOMAIN, device_id))
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="",
                data={
                    CONF_DEVICE_ID: device_id,
                    CONF_TOPIC_PREFIX: topic_prefix,
                    CONF_TIME_ZONE_ELECTRICITY: time_zone_electricity,
                    CONF_TIME_ZONE_GAS: time_zone_gas,
                })

        get_timezones: list[str] = list(
            await self.hass.async_add_executor_job(
                zoneinfo.available_timezones
            )
        )
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required(CONF_DEVICE_ID, default=DEFAULT_DEVICE_ID):str,
                vol.Required(CONF_TOPIC_PREFIX, default=DEFAULT_TOPIC_PREFIX):str,
                vol.Required(CONF_TIME_ZONE_ELECTRICITY, default=self.hass.config.time_zone): SelectSelector(
                    SelectSelectorConfig(
                        options=get_timezones, mode=SelectSelectorMode.DROPDOWN, sort=True
                    )
                ),
                vol.Required(CONF_TIME_ZONE_GAS, default=self.hass.config.time_zone): SelectSelector(
                    SelectSelectorConfig(
                        options=get_timezones, mode=SelectSelectorMode.DROPDOWN, sort=True
                    )
                ),
            }), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return HildebrandGlowIHDMQTTOptionsFlowHandler()

class HildebrandGlowIHDMQTTOptionsFlowHandler(OptionsFlow):
    """Handle a option flow for HildebrandGlowIHDMQTT."""

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        get_timezones: list[str] = list(
            await self.hass.async_add_executor_job(
                zoneinfo.available_timezones
            )
        )
        data_schema=vol.Schema({
            vol.Required(CONF_DEVICE_ID, default=self.config_entry.options.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID)):str,
            vol.Required(CONF_TOPIC_PREFIX, default=self.config_entry.options.get(CONF_TOPIC_PREFIX, DEFAULT_TOPIC_PREFIX)):str,
            vol.Required(CONF_TIME_ZONE_ELECTRICITY, default=self.config_entry.options.get(CONF_TIME_ZONE_ELECTRICITY, self.hass.config.time_zone)): SelectSelector(
                SelectSelectorConfig(
                    options=get_timezones, mode=SelectSelectorMode.DROPDOWN, sort=True
                )
            ),
            vol.Required(CONF_TIME_ZONE_GAS, default=self.config_entry.options.get(CONF_TIME_ZONE_GAS, self.hass.config.time_zone)): SelectSelector(
                SelectSelectorConfig(
                    options=get_timezones, mode=SelectSelectorMode.DROPDOWN, sort=True
                )
            ),
        })
        return self.async_show_form(step_id="init", data_schema=data_schema)
