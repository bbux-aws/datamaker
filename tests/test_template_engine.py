import os
import dataspec.template_engines as engines


def test_basic_template():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    engine = engines.load(dir_path + '/data/template.jinja')

    rendered = engine.process({'A': 1, 'B': 2, 'C': 3, '_internal': {'_iteration': 1}})

    assert 'A:1, B:2, C:3' in rendered
