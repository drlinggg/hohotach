"""Configs are defined here"""

from __future__ import annotations

import os
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO

import yaml


@dataclass
class ClientConfig:
    host: str
    port: int

@dataclass
class TelethonConfig:
    api_id: int
    api_hash: str

@dataclass
class TelegramClientConfig:
    telethon: TelethonConfig
    client: ClientConfig



@dataclass
class HohotachConfig:
    vim_client: ClientConfig
    telegram_client: TelegramClientConfig


    def to_order_dict(self) -> OrderedDict:
        """OrderDict transformer."""

        def to_ordered_dict_recursive(obj) -> OrderedDict:
            """Recursive OrderDict transformer."""

            if isinstance(obj, (dict, OrderedDict)):
                return OrderedDict((k, to_ordered_dict_recursive(v)) for k, v in obj.items())
            if hasattr(obj, "__dataclass_fields__"):
                return OrderedDict(
                    (field, to_ordered_dict_recursive(getattr(obj, field))) for field in obj.__dataclass_fields__
                )
            return obj

        return OrderedDict(
            [
                ("vim_client", to_ordered_dict_recursive(self.vim_client)),
                ("telegram_client", to_ordered_dict_recursive(self.telegram_client)),
            ]
        )

    def dump(self, file: str | Path | TextIO) -> None:
        """Export current configuration to a file"""

        class OrderedDumper(yaml.SafeDumper):
            def represent_dict_preserve_order(self, data):
                return self.represent_dict(data.items())

        OrderedDumper.add_representer(OrderedDict, OrderedDumper.represent_dict_preserve_order)

        if isinstance(file, (str, Path)):
            with open(str(file), "w", encoding="utf-8") as file_w:
                yaml.dump(self.to_order_dict(), file_w, Dumper=OrderedDumper, default_flow_style=False)
        else:
            yaml.dump(self.to_order_dict(), file, Dumper=OrderedDumper, default_flow_style=False)

    @classmethod
    def example(cls) -> "HohotachConfig":
        """Generate an example of configuration."""

        return cls(
            vim_client=ClientConfig(host='127.0.0.1', port=12345),
            telegram_client=TelegramClientConfig(
                telethon=TelethonConfig(
                    api_id=1,
                    api_hash='1',
                    ),
                client=ClientConfig(
                    host='127.0.0.1',
                    port=12346,
                )
            )
        )

    @classmethod
    def load(cls, file: str | Path | TextIO) -> "HohotachConfig":
        """Import config from the given filename or raise `ValueError` on error."""

        try:
            if isinstance(file, (str, Path)):
                with open(file, "r", encoding="utf-8") as file_r:
                    data = yaml.safe_load(file_r)
            else:
                data = yaml.safe_load(file)

            telegram_client = data.get("telegram_client", {})
            return cls(
                vim_client=ClientConfig(**data.get("vim_client", {})),
                telegram_client=TelegramClientConfig(
                    client=ClientConfig(**telegram_client["client"]),
                    telethon=TelethonConfig(
                        **telegram_client["telethon"],
                    ),
                ),
            )
        except Exception as exc:
            raise ValueError(f"Could not read app config file: {file}") from exc

    @classmethod
    def from_file_or_default(cls) -> "HohotachConfig":
        """Try to load configuration from the path specified in the environment variable."""

        config_path: str = os.getenv("CONFIG_PATH")

        if not config_path:
            return cls.example()

        return cls.load(config_path)
