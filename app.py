import aha_zen_adapter

import aha_zen_master_feature_importer

import slack_sender


feature_update=aha_zen_adapter.main()
slack_sender.send_message(slack_sender.features_format_message(feature_update))
master_feature_update=aha_zen_master_feature_importer.main()
slack_sender.send_message(str(master_feature_update))

