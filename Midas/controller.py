import docker
import click
import os


@click.command()
@click.argument('image')
@click.argument('args', nargs=-1)
def main(image, args):
    try:
        # check if the image already exists, no need to rebuild
        docker_img = client.images.get(image)
    except docker.errors.ImageNotFound:
        # find the location of the image
        # build
        docker_img = client.images.build(path=f"{os.getcwd()}/{image}/.")

    # run
    client.containers.run(
        docker_img[0],
        ['python', 'main.py'] + list(args),
        network="databases_default",
    )


if __name__ == "__main__":
    client = docker.from_env()
    main()
