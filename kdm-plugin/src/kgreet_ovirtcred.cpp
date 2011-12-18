
#include "kgreet_ovirtcred.h"
#include "OVirtCred.h"

#include <kglobal.h>
#include <klocale.h>

#include <QtGui/QLayout>
#include <QtGui/QLabel>

#define KDM_OVIRTCRED_SERVER_DBUS_NAME      "org.ovirt.vdsm.Credentials"
#define KDM_OVIRTCRED_SERVER_DBUS_PATH      "/org/ovirt/vdsm/Credentials"
#define KDM_OVIRTCRED_SERVER_DBUS_INTERFACE KDM_OVIRTCRED_SERVER_DBUS_NAME

KOVirtCredGreeter::KOVirtCredGreeter(KGreeterPluginHandler *handler,
                                   QWidget *parent,
                                   const QString &fixedEntity,
                                   Function func, Context ctx) :
    QObject(),
    KGreeterPlugin(handler)
{
    Q_UNUSED(parent);
    Q_UNUSED(fixedEntity);
    Q_UNUSED(func);
    Q_UNUSED(ctx);

    parent = new QWidget(parent);
    parent->setObjectName("welcome");
    widgetList << parent;

    QBoxLayout *grid = new QBoxLayout(QBoxLayout::LeftToRight, parent);
    m_titleLabel = new QLabel(i18n("oVirt Automatic Login System"), parent);
    grid->addWidget(m_titleLabel, 0, Qt::AlignHCenter);    

    m_Credentials = new OVirtCred(KDM_OVIRTCRED_SERVER_DBUS_NAME, KDM_OVIRTCRED_SERVER_DBUS_PATH,
        QDBusConnection::systemBus(), 0);
        
    QObject::connect(m_Credentials, SIGNAL(UserAuthenticated(QString)),
        this, SLOT(userAuthenticated(QString)));
}

KOVirtCredGreeter::~KOVirtCredGreeter()
{
    abort();
    qDeleteAll(widgetList);

    delete m_Credentials;
}

void KOVirtCredGreeter::loadUsers(const QStringList &users)
{
    // We do no offer a selectable users list.
    Q_UNUSED(users);
}

void KOVirtCredGreeter::presetEntity(const QString &entity, int field)
{
    // We do not care about preloaded users either.
    Q_UNUSED(entity);
    Q_UNUSED(field);
}

QString KOVirtCredGreeter::getEntity() const
{
    return QString();
}

void KOVirtCredGreeter::setUser(const QString &user)
{
    Q_UNUSED(user);
}

void KOVirtCredGreeter::setEnabled(bool on)
{
    Q_UNUSED(on);
}

bool KOVirtCredGreeter::textMessage(const char *message, bool error)
{
    if (error) {
        // Stop authentication.
        abort();
    } else {
        handler->gplugMsgBox(QMessageBox::Information, message);
    }

    return true;
}

void KOVirtCredGreeter::textPrompt(const char *prompt, bool echo, bool nonBlocking)
{
    Q_UNUSED(echo);
    Q_UNUSED(nonBlocking);
    
    QString text = QString(prompt);
    if (text.contains(QString("Token?"), Qt::CaseInsensitive)) {
        handler->gplugReturnText(m_token.toAscii(), KGreeterPluginHandler::IsSecret);
        m_token.clear();
    } else {
        abort();
    }
}

bool KOVirtCredGreeter::binaryPrompt(const char *prompt, bool nonBlocking)
{
    Q_UNUSED(prompt);
    Q_UNUSED(nonBlocking);
    return true;
}

void KOVirtCredGreeter::start()
{

}

void KOVirtCredGreeter::suspend()
{

}

void KOVirtCredGreeter::resume()
{

}

void KOVirtCredGreeter::next()
{

}

void KOVirtCredGreeter::abort()
{

}

void KOVirtCredGreeter::succeeded()
{

}

void KOVirtCredGreeter::failed()
{

}

void KOVirtCredGreeter::revive()
{

}

void KOVirtCredGreeter::clear()
{

}

void KOVirtCredGreeter::userAuthenticated(QString token)
{
    m_token = token;
    
    handler->gplugStart();
}

static bool init(const QString &,
                 QVariant (*getConf)(void *, const char *, const QVariant &),
                 void *ctx)
{
    Q_UNUSED(getConf);
    Q_UNUSED(ctx);
    KGlobal::locale()->insertCatalog("kgreet_ovirtcred");
    return true;
}

static void done()
{
    KGlobal::locale()->removeCatalog("kgreet_ovirtcred");
}

static KGreeterPlugin* create(KGreeterPluginHandler *handler,
                              QWidget *parent,
                              const QString &fixedEntity,
                              KGreeterPlugin::Function func,
                              KGreeterPlugin::Context ctx)
{
    return new KOVirtCredGreeter(handler, parent, fixedEntity, func, ctx);
}

KDE_EXPORT KGreeterPluginInfo kgreeterplugin_info = {
    I18N_NOOP2("@item:inmenu authentication method", "oVirt Authentication"), "ovirtcred",
    KGreeterPluginInfo::Local | KGreeterPluginInfo::Presettable,
    init, done, create
};

#include "kgreet_ovirtcred.moc"
