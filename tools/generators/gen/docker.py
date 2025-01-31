import re


class DockerImage:
    # Use double-hash for parser directives
    COMMENT_REGEX = re.compile(rf"^\s*#($|[^#].*)")

    _IMAGE_CLASS = r"[\w\-\.:]"
    FROM_REGEX = re.compile(
        rf"^\s*"
        rf"FROM\s+(?P<from>{_IMAGE_CLASS}+)\s+"
        rf"AS\s+(?P<as>json-ci-{_IMAGE_CLASS}+)"
    )

    registry = {}
    roots = []

    # @staticmethod
    # def _get_images_from_source(source, filename=None):
    #     lines = source.split("\n")
    #     images = []
    #     for line in lines:
    #         if match := DockerImage.FROM_REGEX.match(line):
    #             from_lines += 1
    #             images.append(
    #                 DockerImage(
    #                     match.group("as"),
    #                     match.group("from"),
    #                     filename,
    #                     source,
    #                 )
    #             )

    # @staticmethod
    # def _from_dockerfile(dockerfile, register=True):
    #     pass

    # @staticmethod
    # def _from_dockerfile_source(source, filename, register=True):
    #     pass

    @staticmethod
    def from_dockerfile(dockerfile, source=None, with_source=True, register=True):
        if dockerfile and not source:
            with open(dockerfile, "r") as f:
                source = f.read()

        from_lines = 0
        lines = source.split("\n")
        images = []
        for line in lines:
            if match := DockerImage.FROM_REGEX.match(line):
                from_lines += 1
                images.append(
                    DockerImage(
                        match.group("as"),
                        match.group("from"),
                        dockerfile,
                        source if with_source else None,
                    )
                )

        if with_source and from_lines != 1:
            raise RuntimeError(
                f"Expected exactly one FROM instruction, found {from_lines}."
            )

        if register:
            for image in images:
                DockerImage.register(image)

        return images

    @staticmethod
    def register(image):
        DockerImage.registry[image.name] = image

    @staticmethod
    def get(name):
        return DockerImage.registry.get(name, None)

    @staticmethod
    def solve_dependencies():
        # resolve parent names to objects
        for image in DockerImage.registry.values():
            image.parent = DockerImage.get(image.parent)

        # find images that are not themselves dependencies and are to be generated
        parents = set(
            image.parent.name for image in DockerImage.registry.values() if image.parent
        )
        roots = [
            image
            for image in DockerImage.registry.values()
            if image.generate and not image.name in parents
        ]

        # build dependency graphs via depth-first search
        for root in roots:
            graph = []
            visited = set()

            def visit(image):
                if image.name not in visited:
                    visited.add(image.name)
                    if image.parent and isinstance(image.parent, str):
                        image.parent = DockerImage.get(image.parent)
                if image.parent:
                    visit(image.parent)
                graph.append(image)

            # start depth-first search
            visit(root)
            root.is_root = True
            root.dependencies = list(reversed(graph[:-1]))

        DockerImage.roots = roots

    @staticmethod
    def normalize_filenames(root_dir):
        for image in DockerImage.registry.values():
            image.dockerfile = image.dockerfile.relative_to(root_dir)

    def __init__(self, name, parent, dockerfile, source=None):
        self.name = name
        self.real_parent = parent
        self.parent = parent
        self.dockerfile = dockerfile
        self.source = source
        self.generate = True
        self.publish = True
        self.is_root = False
        self.dependencies = []

    def __repr__(self):
        parent = (
            self.parent.name if isinstance(self.parent, DockerImage) else self.parent
        )
        return f"DockerImage({self.name}, parent={parent})"
