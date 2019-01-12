from typing import Tuple, Optional, List

from deeppavlov import train_model
from deeppavlov import build_model
from deeppavlov.core.common.log import get_logger
from deeppavlov.core.skill.skill import Skill
from deeppavlov.core.common.file import read_json
from deeppavlov.core.common.file import find_config
from deeppavlov.core.data.utils import update_dict_recursive

log = get_logger(__name__)


class IntentMatchingSkill(Skill):
    """Skill, matches utterances to intents, returns predefined answers.

    Allows to create skills that give answers to corresponding intents
    Skill returns response and confidence.

    Args:
        data_path: URL or local path to '.csv' file that contains two columns with Intents and Answers.
            User's utterance will be compared with Intents column and respond will be selected
            from matching row from Answers column.
        x_col_name: Name of the column in '.csv' file, that represents Intents column.
        y_col_name: Name of the column in '.csv' file, that represents Answer column.
        edit_dict: Dictionary of edits in config
        save_load_path: Path, where model will be saved or loaded from
        train: Should model be trained or not

    Attributes:
        model: Classifies user's questions
    """

    def __init__(self, data_path: Optional[str] = None,
                 x_col_name: Optional[str] = None, y_col_name: Optional[str] = None,
                 edit_dict: Optional[dict] = None, save_load_path: Optional[str] = None, train: bool = True):

        model_config = read_json(find_config('tfidf_autofaq'))
        if x_col_name is not None:
            model_config['dataset_reader']['x_col_name'] = x_col_name
        if y_col_name is not None:
            model_config['dataset_reader']['y_col_name'] = y_col_name

        if save_load_path is None:
            save_load_path = './faq'
        model_config['metadata']['variables']['ROOT_PATH'] = save_load_path

        if data_path is not None:
            if 'data_url' in model_config['dataset_reader']:
                del model_config['dataset_reader']['data_url']
            model_config['dataset_reader']['data_path'] = data_path

        if edit_dict is not None:
            update_dict_recursive(model_config, edit_dict)

        if train:
            self.model = train_model(model_config)
            log.info('Your model was saved at: \'' + save_load_path + '\'')
        else:
            self.model = build_model(model_config)

    def __call__(self, utterances_batch: List[str], history_batch: List[List[str]],
                 states_batch: Optional[list] = None) -> Tuple[List[str], List[float]]:
        """Returns skill inference result.

        Returns batches of skill inference results and estimated confidence levels

        Args:
            utterances_batch: A batch of utterances of any type.
            history_batch: A batch of list typed histories for each utterance.
            states_batch: Optional. A batch of arbitrary typed states for
                each utterance.

        Returns:
            response: A batch of arbitrary typed skill inference results.
            confidence: A batch of float typed confidence levels for each of
                skill inference result.
        """
        return self.model(utterances_batch)