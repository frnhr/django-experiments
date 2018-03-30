# coding=utf-8
from __future__ import absolute_import

from model_mommy import mommy
from unittest import TestCase

from experiments.conditional.enrollment import Experiments
from experiments.tests.testing_2_3 import mock


class ConditionalEnrollmentTestCase(TestCase):
    maxDiff = None

    def setUp(self):
        self.request = mock.MagicMock()
        self.context = {'request': self.request}
        self.experiments = Experiments(self.context)

    def test_report(self):
        instance = mock.MagicMock()
        instance.name = "mock_experiment"
        active = True
        variate = 'mock_variate'
        self.experiments._report(instance, active, variate)
        self.assertIn(
            'mock_experiment', self.experiments.report['conditional'])
        expected_report = {
            'disabled': False,
            'enrolled_alternative': 'mock_variate',
        }
        self.assertEqual(
            expected_report,
            self.experiments.report['conditional']['mock_experiment']
        )

    def test_evaluate_conditionals_wo_instances(self):
        self.experiments.experiment_names = []
        self.experiments.report = {'conditional': {}}
        with mock.patch.object(self.experiments, 'get_participant'):
            self.experiments._evaluate_conditionals()
            self.experiments.get_participant.assert_not_called()
        expected_report = {'conditional': {}}
        self.assertEqual(expected_report, self.experiments.report)

    @mock.patch('experiments.conditional.enrollment.experiment_manager')
    def test_evaluate_conditionals_w_instances(self, experiment_manager):
        i1, i2 = mock.MagicMock(), mock.MagicMock()
        i1.name = 'mock_exp_1'
        i1.default_alternative = 'variate_for_exp_1'
        i2.name = 'mock_exp_2'
        i1.is_enabled_by_conditionals.return_value = False
        i2.is_enabled_by_conditionals.return_value = True
        self.experiments.experiment_names = [i1.name, i2.name]
        self.experiments.report = {'conditional': {}}
        experiment_manager.get_experiment.side_effect = [i1, i2]
        self.experiments._evaluate_conditionals()
        expected_report = {
            'conditional': {
                'mock_exp_1': {
                    'disabled': True,
                    'enrolled_alternative': 'variate_for_exp_1',
                },
                'mock_exp_2': {
                    'disabled': False,
                    'enrolled_alternative': None,
                },
            },
        }
        self.assertEqual(expected_report, self.experiments.report)
        expected_list = ['mock_exp_1', ]
        self.assertEqual(expected_list, self.experiments.disabled_experiments)

    @mock.patch('experiments.conditional.enrollment.experiment_manager')
    def test_evaluate_conditionals_wo_experiments(self, experiment_manager):
        i1, i2 = mock.MagicMock(), mock.MagicMock()
        i1.name = 'mock_exp_1'
        i1.default_alternative = 'variate_for_exp_1'
        i2.name = 'mock_exp_2'
        i1.is_enabled_by_conditionals.return_value = False
        i2.is_enabled_by_conditionals.return_value = True
        self.experiments.experiment_names = [i1.name, i2.name]
        self.experiments.report = {'conditional': {}}
        experiment_manager.get_experiment.side_effect = [None, None]
        self.experiments._evaluate_conditionals()
        self.assertEqual({'conditional': {}}, self.experiments.report)


class ConditionalEnrollmentWithDataTest(TestCase):

    def setUp(self):
        self.request = mock.MagicMock()
        self.context = {'request': self.request}

    def test_evaluate_conditionals_w_instances_no_patching(self):
        exp1_alternatives = {
            'variate_for_exp_1': {
                'default': True, 'enabled': True, 'weight': 50
            },
            'control': {'enabled': True, 'weight': 50},
        }
        exp1 = mommy.make(
            'experiments.Experiment',
            name='exp_1',
            alternatives=exp1_alternatives)
        exp2 = mommy.make('experiments.Experiment', name='exp_2')  # noqa
        mommy.make(
            'experiments.AdminConditional',
            experiment=exp1)
        experiments = Experiments(self.context)
        expected_report = {
            'conditional': {
                'exp_1': {
                    'disabled': True,
                    'enrolled_alternative': 'variate_for_exp_1',
                },
                'exp_2': {
                    'disabled': False,
                    'enrolled_alternative': None,
                },
            },
        }
        self.assertEqual(experiments.report, expected_report)
        disabled_list = ['exp_1', ]
        self.assertEqual(experiments.disabled_experiments, disabled_list)
